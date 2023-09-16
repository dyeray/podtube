import datetime

import responses

from plugins.ivoox import PluginImpl


def test_get_feed(utils):
    channel_id = 'podcast-podcast-podcast-campamento-krypton_sq_f167429_1'
    expected_url = f'https://www.ivoox.com/{channel_id}.html'
    responses.add(responses.GET, expected_url, body=utils.get_fixture('ivoox.html'), status=200, content_type='text/html; charset=UTF-8')

    plugin = PluginImpl({})
    feed = plugin.get_feed(channel_id)
    episode = feed.items[0]

    assert feed.feed_id == channel_id
    assert feed.link == f'https://www.ivoox.com/{channel_id}.html'
    assert feed.title == 'Campamento Krypton'
    assert feed.description == 'Un podcast donde la cultura pop brilla, burbujea y se alborota. Monográficos y entrevistas sobre cine, cómic, música, empanadillas y Lina Morgan. Organizadores y creadores de la Monstrua de Cine Chungo, también podías escucharnos en Efecto Doppler (Radio 3)'
    assert feed.image == 'http://static-1.ivoox.com/canales/7/9/8/0/901603780897_XXL.jpg'
    assert len(feed.items) == 14 # Ignores 6 paid episodes

    assert episode.item_id == 'ck-227-navidades-infernales-de-black-christmas-a-krampus-audios-mp3_rf_79593896_1'
    assert episode.title == 'CK#227: Navidades infernales: De Black Christmas a Krampus'
    assert episode.description == 'Cenas de empresa, galas televisivas, consumismo desaforado, villancicos, símbolos inquietantes... En Navidad hay motivos para el terror y el cine ha sabido aprovecharlos.\r\n\r\nRepasamos el cine de terror navideño con cintas pioneras del slasher como Black Christmas, sagas como Noche de paz, noche de muerte, perversiones de Papa Noel como Rare Exports, monstruos como el Krampus y hasta muñecos de nieve asesinos como Jack Frost. \r\n\r\n¡Felices Fiestas!\r\n\r\nPrograma patrocinado por Xiaomi 11T. Descubre el móvil de cine que tiene todo lo que necesitas y más.\r\nhttps://www.mi.com/es/product/xiaomi-11t/\r\n'
    assert episode.date.date() == datetime.date(2021, 12, 20)
    assert episode.image == 'https://img-static.ivoox.com/index.php?w=77&h=77&url=https://static-2.ivoox.com/audios/1/0/4/2/4431639522401_XXL.jpg'
    assert episode.content_type == 'audio/mp4'
