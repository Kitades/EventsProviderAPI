import pytest
from unittest.mock import AsyncMock, MagicMock
from app.usecases import CreateTicketUsecase

@pytest.mark.asyncio
async def test_ticket_creation_prevented_for_cancelled_event():
    mock_client = AsyncMock()
    mock_event_repo = AsyncMock()

    # Имитируем отмененное событие в базе
    cancelled_event = MagicMock()
    cancelled_event.status = "cancelled"
    mock_event_repo.get_by_id.return_value = cancelled_event

    usecase = CreateTicketUsecase(mock_client, mock_event_repo)

    # Ожидаем исключение
    with pytest.raises(Exception, match="Регистрация невозможна"):
        await usecase.execute("ev-id", "Ivan", "Ivanov", "A1")

    # Проверяем, что запрос на регистрацию НЕ ушел в API
    mock_client.register.assert_not_called()