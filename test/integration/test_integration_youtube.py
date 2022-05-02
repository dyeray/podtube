import datetime

import responses

from plugins.youtube import ServiceImpl


def test_get_feed(utils):
    channel_id = 'UCk195x4zYdMx4LhqEwhcPng'
    expected_url = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'
    responses.add(responses.GET, expected_url, body=utils.get_fixture('youtube.xml'), status=200, content_type='text/xml; charset=UTF-8')
    expected_episode_id = 'Elewn679CZI'

    service = ServiceImpl({})
    feed = service.get_feed(channel_id)
    episode = feed.items[0]
    assert feed.feed_id == channel_id
    assert feed.title == 'Instituto de Física Teórica IFT'
    assert feed.description == 'Instituto de Física Teórica IFT'
    assert feed.link == f'https://www.youtube.com/channel/{channel_id}'
    assert feed.image == ''

    assert episode.item_id == expected_episode_id
    assert episode.title == 'El Brillante Futuro de la Física | Una Conversación con Álvaro de Rújula'
    assert episode.description == 'Álvaro de Rújula, referente a nivel mundial en el área de la Física Fundamental a lo largo de las últimas décadas, nos explica en una conversación con J.L.F. Barbón sus experiencias, anécdotas e hitos científicos en su carrera en las más prestigiosas instituciones, como la U. Harvard y el CERN.\n\nCharla en la Residencia de Estudiantes de Madrid por la Semana de la Ciencia 2021.\n\nÁlvaro de Rújula es un referente a nivel mundial en el área de la Física Fundamental a lo largo de las últimas décadas. Ha sido profesor en las más prestigiosas instituciones, como la Universidad de Harvard, y Director del grupo de Física Teórica del CERN. En la elite investigadora durante los últimos 50 años, ha conocido de primera mano y contribuido significativamente a varios de los logros fundacionales del Modelo Estándar, las leyes fundamentales que rigen el comportamiento de las partículas elementales. \n\nComo investigador reconocido a nivel internacional, y excelente comunicador y divulgador de la Ciencia, nos explicará su experiencia explorando los misterios del universo, su perspectiva de la Física en las últimas décadas, y su visión de futuro sobre las cuestiones abiertas más importantes en este campo.\n\nCRÉDITOS:\n\nArtículo José Adolfo de Azcárraga\nhttps://www.elconfidencial.com/espana/2021-10-14/entrevista-azcarraga-educacion-analfabetismo-matematico_3306110/\n\nArtículo Nature\nhttps://www.nature.com/articles/320678a0.pdf\n\nArtículo  evolución de la estructura del protón con la energía\nhttps://journals.aps.org/prd/abstract/10.1103/PhysRevD.10.2141\n\nArtículo Lambda QCD\nhttps://journals.aps.org/prl/abstract/10.1103/PhysRevLett.32.1143\n\nElementary, Dear Albert!\nCERN\nhttps://www.youtube.com/watch?v=iTWI-jV8HJY'
    assert episode.image == 'https://i2.ytimg.com/vi/Elewn679CZI/hqdefault.jpg'
    assert episode.content_type == 'video/mp4'
    assert episode.date.date() == datetime.date(2021, 12, 19)
