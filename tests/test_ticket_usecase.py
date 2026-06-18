from unittest.mock import AsyncMock, MagicMock
import uuid

import pytest

from app.models import EventStatus
from app.usecases import CancelTicketUsecase, CreateTicketUsecase


@pytest.mark.asyncio
async def test_create_ticket_success():
    event_id = uuid.uuid4()
    mock_client = AsyncMock()
    mock_client.register.return_value = 'ticket-123'
    mock_event_repo = AsyncMock()
    mock_event_repo.get_by_id.return_value = MagicMock(
        status=EventStatus.published.value
    )
    mock_ticket_repo = AsyncMock()

    usecase = CreateTicketUsecase(mock_client, mock_event_repo, mock_ticket_repo)
    result = await usecase.execute(event_id, 'Ivan', 'Ivanov', 'test@example.com', 'A1')
    assert result == 'ticket-123'
    mock_ticket_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_ticket_event_not_found():
    mock_client = AsyncMock()
    mock_event_repo = AsyncMock()
    mock_event_repo.get_by_id.return_value = None
    mock_ticket_repo = AsyncMock()

    usecase = CreateTicketUsecase(mock_client, mock_event_repo, mock_ticket_repo)
    with pytest.raises(ValueError, match='Event not found'):
        await usecase.execute(uuid.uuid4(), 'Ivan', 'Ivanov', 'test@example.com', 'A1')


@pytest.mark.asyncio
async def test_create_ticket_event_not_published():
    mock_client = AsyncMock()
    mock_event_repo = AsyncMock()
    event = MagicMock(status='cancelled')
    mock_event_repo.get_by_id.return_value = event
    mock_ticket_repo = AsyncMock()

    usecase = CreateTicketUsecase(mock_client, mock_event_repo, mock_ticket_repo)
    with pytest.raises(ValueError, match='Registration is not possible'):
        await usecase.execute(uuid.uuid4(), 'Ivan', 'Ivanov', 'test@example.com', 'A1')


@pytest.mark.asyncio
async def test_cancel_ticket_success():
    ticket_id = uuid.uuid4()
    mock_client = AsyncMock()
    mock_client.cancel_registration.return_value = True
    mock_ticket_repo = AsyncMock()
    ticket = MagicMock(event_id=uuid.uuid4())
    mock_ticket_repo.get.return_value = ticket

    usecase = CancelTicketUsecase(mock_client, mock_ticket_repo)
    result = await usecase.execute(str(ticket_id))
    assert result is True
    mock_client.cancel_registration.assert_awaited_once_with(
        ticket.event_id, str(ticket_id)
    )
    mock_ticket_repo.delete.assert_awaited_once_with(ticket_id)


@pytest.mark.asyncio
async def test_cancel_ticket_not_found():
    mock_client = AsyncMock()
    mock_ticket_repo = AsyncMock()
    mock_ticket_repo.get.return_value = None

    usecase = CancelTicketUsecase(mock_client, mock_ticket_repo)
    result = await usecase.execute(str(uuid.uuid4()))
    assert result is False
    mock_client.cancel_registration.assert_not_awaited()
