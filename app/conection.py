"""
КЛАСС EventsProviderClient:
    ФУНКЦИЯ get_events(changed_at):
        ОТПРАВИТЬ GET {EXTERNAL_API_URL}/events?changed_at={changed_at}
        ВЕРНУТЬ список объектов событий

    ФУНКЦИЯ get_seats(event_id):
        ОТПРАВИТЬ GET {EXTERNAL_API_URL}/events/{event_id}/seats
        ВЕРНУТЬ список мест

    ФУНКЦИЯ register_ticket(data):
        ОТПРАВИТЬ POST {EXTERNAL_API_URL}/tickets С ТЕЛОМ {data}
        ВЕРНУТЬ ID билета или ОШИБКУ
"""