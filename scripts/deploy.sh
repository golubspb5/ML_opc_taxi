#!/usr/bin/env bash
set -euo pipefail

NEW_TAG="$1"
COMPOSE_FILE="docker-compose.yml"
NGINX_CONF_DIR="nginx/nginx"
PROJECT_NAME="ml"

if [ -z "${NEW_TAG:-}" ]; then
  echo "❌ ERROR: NEW_TAG is empty. Usage: ./deploy.sh <IMAGE_TAG>"
  exit 1
fi

# 1. Определяем активный цвет
if grep -E '^[[:space:]]*server[[:space:]]+ml-app-blue' "${NGINX_CONF_DIR}/upstream.conf" >/dev/null 2>&1; then
  ACTIVE_COLOR="blue"
  NEW_COLOR="green"
  OLD_COLOR="blue"
else
  ACTIVE_COLOR="green"
  NEW_COLOR="blue"
  OLD_COLOR="green"
fi

echo "Active color: $ACTIVE_COLOR"
echo "New color:    $NEW_COLOR"
echo "Old color:    $OLD_COLOR"
echo "Using image tag: $NEW_TAG"

# 2. Проставляем теги образов для docker-compose
export BLUE_TAG="$NEW_TAG"
export GREEN_TAG="$NEW_TAG"

# 3. Убедимся, что proxy запущен (если нет — поднимаем)
if ! docker ps --format '{{.Names}}' | grep -q '^ml-proxy$'; then
  echo "Proxy container not found, starting it..."
  docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" up -d proxy
else
  echo "Proxy container ml-proxy already running, will not recreate."
fi

# 4. Чистим контейнер нового цвета (если был)
echo "Cleaning stale container for new color: $NEW_COLOR"
docker rm -f "ml-app-${NEW_COLOR}" >/dev/null 2>&1 || true

# 5. Подтягиваем и поднимаем новую ревизию для нового цвета
echo "Pulling new image for ml-app-${NEW_COLOR}..."
docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" pull "app_${NEW_COLOR}"

echo "Starting new ml-app-${NEW_COLOR}..."
docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" up -d "app_${NEW_COLOR}"

# 6. Ждём HEALTHCHECK нового контейнера
echo "Waiting for ml-app-${NEW_COLOR} to be healthy..."
ATTEMPTS=20
SLEEP_SEC=3

for i in $(seq 1 $ATTEMPTS); do
  STATUS=$(docker inspect --format='{{json .State.Health.Status}}' "ml-app-${NEW_COLOR}" 2>/dev/null || echo "\"starting\"")
  echo "Health status: $STATUS"
  if [ "$STATUS" = "\"healthy\"" ]; then
    echo "✅ New version ml-app-${NEW_COLOR} is healthy!"
    break
  fi
  sleep "$SLEEP_SEC"
done

if [ "$STATUS" != "\"healthy\"" ]; then
  echo "❌ ERROR: New version ml-app-${NEW_COLOR} did not become healthy."
  echo "Rolling back: stopping bad container..."
  docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" stop "app_${NEW_COLOR}" || true
  echo "Rollback complete. Old version kept."
  exit 1
fi

# 7. Переключаем Nginx на новый цвет
echo "Switching nginx upstream to: $NEW_COLOR"
cp "${NGINX_CONF_DIR}/upstream_${NEW_COLOR}.tmpl" "${NGINX_CONF_DIR}/upstream.conf"

echo "Reloading nginx..."
docker exec ml-proxy nginx -s reload

# 8. Дополнительная проверка после переключения трафика
echo "Verifying new version via nginx (http://localhost/)..."
sleep 5

if ! curl -fs http://localhost/ > /dev/null; then
  echo "❌ New version failed AFTER nginx switch. Rolling back..."

  # возвращаем старый upstream
  cp "${NGINX_CONF_DIR}/upstream_${OLD_COLOR}.tmpl" "${NGINX_CONF_DIR}/upstream.conf"
  docker exec ml-proxy nginx -s reload

  # гасим новый проблемный цвет
  docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" stop "app_${NEW_COLOR}" || true

  echo "Rollback done. Traffic restored to ${OLD_COLOR}."
  exit 1
fi

# 9. Если всё ок — гасим старую версию
echo "Stopping old version: ml-app-${OLD_COLOR}"
docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" stop "app_${OLD_COLOR}" || true

echo "🎉 SUCCESS: Blue-Green deploy complete!"
