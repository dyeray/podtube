import datetime

import responses

from plugins.invidious import PluginImpl


def test_get_feed_channel(utils):
    channel_id = 'UCk195x4zYdMx4LhqEwhcPng'
    expected_url = f'https://invidious.namazso.eu/feed/channel/{channel_id}'
    responses.add(responses.GET, expected_url, body=utils.get_fixture('invidious_channel.xml'), status=200, content_type='text/xml; charset=UTF-8')
    expected_episode_id = 'dpkt5MmlWZY'

    plugin = PluginImpl({})
    feed = plugin.get_feed(channel_id)
    episode = feed.items[0]
    assert feed.feed_id == channel_id
    assert feed.title == 'Instituto de Física Teórica IFT'
    assert feed.description == 'Instituto de Física Teórica IFT'
    assert feed.link == f'https://invidious.namazso.eu/channel/{channel_id}'
    assert feed.image == 'https://yt3.ggpht.com/ytc/AKedOLQ1m7mh1IRDdXuiZ0J2IuVGDAo7EcfkbWewhP4pHA=s900-c-k-c0x00ffffff-no-rj'

    assert episode.item_id == expected_episode_id
    assert episode.title == '¿Por Qué Todo OSCILA en el Universo? | El OSCILADOR ARMÓNICO'
    assert episode.description == 'Desde las cuerdas de un violín hasta el plasma ardiente del universo primitivo, pasando por los campos cuánticos y las ondas gravitacionales, TODO oscila en el universo. Angel Uranga nos explica que detrás de estos patrones se esconde el concepto posiblemente más influyente de la Historia de la Física: el oscilador armónico. \n#Oscilador#Armonico\n\nNo te pierdas ningún vídeo: solo tienes que... ¡SUSCRIBIRTE!, ¡es GRATIS!:\nhttps://www.youtube.com/user/IFTMadrid?sub_confirmation=1\n\n¡Síguenos en TWITTER!            https://www.twitter.com/ift_uam_csic\n¡INSTAGRAM!                      https://www.instagram.com/ift_madrid/\n¡También en FACEBOOK!            https://www.facebook.com/pages/IFT/444787088891187\n¡Y consulta nuestra página web!  https://www.ift.uam-csic.es\n\n\nCRÉDITOS\n\nGalileo\nhttps://www.nuevarevista.net/la-verdad-sobre-el-caso-galileo/\n\nSkate park\nX Games\nhttps://www.youtube.com/watch?v=aEAAWlRFcxo\n\nPéndulo humano Walter Levin\nhttps://www.youtube.com/channel/UCiEHVhv0SBMpP75JbzJShqw\n\nColumpio gran amplitud\nhttps://www.youtube.com/watch?v=zGNCEtg-acY\n\nCaída cuerda\nhttps://www.youtube.com/watch?v=4ec12VKWv_E\n\nReloj\nhttps://www.youtube.com/watch?v=M7s2K1nK7Go\nhttps://www.youtube.com/watch?v=Bs5TziMwwQI\n\nPéndulos desfasados\neclipticom\nhttps://www.youtube.com/watch?v=ihj_tMD_vO4\n\nBungee Jump al agua\nhttps://www.youtube.com/watch?v=Bm1oBkQBMvk\n\nFiguras Lissajous\nhttps://www.youtube.com/watch?v=uPbzhxYTioM\n\nAcrobacia comba\nhttps://www.youtube.com/watch?v=PUWg7fXnCf0\n\nAnimación cuerdas vibrando y columnas de presión\nhttps://ophysics.com/waves6.html\n\nGuitarra, violín\nhttps://www.youtube.com/watch?v=QXjdGBZQvLc\n\nTambor, platillo\nhttps://www.youtube.com/watch?v=QXjdGBZQvLc\n\nSaxo\nhttps://www.youtube.com/watch?v=SWaQdHoCvYk\n\nAire y sonido\nAudiopedia\nhttps://www.youtube.com/watch?v=bYoTRx6gGX0\n\nTímpano\nhttps://www.youtube.com/watch?v=eQEaiZ2j9oc\n\nMuelles y campos cuánticos\nhttps://www.ribbonfarm.com/2015/08/20/qft/\n\n\n\nExtractos de vídeos de J.L.Crespo para IFT\n\nLa Energía Oscura EXPLICADA\nhttps://www.youtube.com/watch?v=ysIQMAjpuYY\n\nLa Teoría de Cuerdas en 7 Minutos\nhttps://www.youtube.com/watch?v=yd1jx1DkXb4\n\n¿Qué Pasó ANTES del Big Bang? | Inflación Cósmica\nhttps://www.youtube.com/watch?v=6n2cw_AW01I\n\nChiken Teriyaki\nRosalía \nMotomami\nhttps://www.youtube.com/watch?v=OG4gq9fCoRE\n\nAtaque a sandía\nKuma Films\nhttps://www.youtube.com/watch?v=WozbZMljRiM\n\nSurf\nhttps://www.youtube.com/watch?v=f6Ltml0uXq4\n\nVacío QCD\nCSSM, Univ. Adelaide, Australia\nhttps://www.youtube.com/watch?v=WZgZI5vymiM\n\nPuente Tacoma\nhttps://www.youtube.com/watch?v=lXyG68_caV4\n\nColumpio\nhttps://www.youtube.com/watch?v=5JbpcsH80us\n\n\nSonido Matrix\nYouToogle\nhttps://www.youtube.com/watch?v=7M06QVsv3S0\n\nMiniatura\nMIKE DUNNING/GETTY\nVia Wired\nhttps://www.wired.com/2016/10/modeling-pendulum-harder-think/'
    assert episode.image == 'https://yewtu.be/vi/dpkt5MmlWZY/mqdefault.jpg'
    assert episode.content_type == 'video/mp4'
    assert episode.date.date() == datetime.date(2022, 4, 21)


def test_get_feed_playlist(utils):
    playlist_id = 'PLH3mdhuA3a24qt8c7fgcbknrLqe5Ijia2'
    expected_url = f'https://invidious.namazso.eu/feed/playlist/{playlist_id}'
    responses.add(responses.GET, expected_url, body=utils.get_fixture('invidious_playlist.xml'), status=200, content_type='text/xml; charset=UTF-8')
    expected_episode_id = '97L58ya1qu8'

    plugin = PluginImpl({'feed_type': 'playlist'})
    feed = plugin.get_feed(playlist_id)
    episode = feed.items[0]
    assert feed.feed_id == playlist_id
    assert feed.title == 'Laberinto de papel'
    assert feed.description == 'Laberinto de papel'
    assert feed.link == f'https://invidious.namazso.eu/playlist?list={playlist_id}'
    assert feed.image == ''

    assert episode.item_id == expected_episode_id
    assert episode.title == "BRUNO PUELLES | Finalista del premio Minotauro por 'SIMBIOSIS'"
    assert episode.description == '⭐️⭐️ Suscríbete a nuestro canal https://bit.ly/3iFHitH ⭐️⭐️\n\nHoy hablamos con Bruno Puelles, uno de los finalistas de los Premios Minotauro por su novela de ciencia ficción "Simbiosis". Una novela híbrida entre ciencia ficción y novela negra, que narra la vida de unos personajes en simbiosis con una especie extraterrestre que llega a la Tierra. \n\n#Laberintodepapel #Minotauro #Literatura\n\nEste contenido es una colaboración y patrocinio entre Xataka y la marca, pero no hay pacto sobre el guión ni la selección de los temas. Esta es la manera que tenemos de generar ingresos en el canal\n\n🔋🔋🔋🔋\n\nSuscríbete http://bit.ly/VIpeW9\n\n📹Echa un vistazo a nuestros vídeos https://www.youtube.com/user/XatakaTV...\n📹Sigue de cerca nuestras playlists https://www.youtube.com/user/XatakaTV...\n\n📰 Newsletter: https://www.getrevue.co/profile/xataka\n🕺🏽 Tiktok https://vm.tiktok.com/ZSt7b3aJ/\n👾 Twitch https://www.twitch.tv/elstream \n📱 La Cacharrería https://www.xataka.com/la-cacharreria/search \n📘Facebook https://www.facebook.com/Xataka\n🕊Twitter http://www.twitter.com/xataka\n📸Instagram http://instagram.com/xataka\n💬Telegram https://t.me/xataka\n🖥Leer más: http://www.xataka.com/\n\n📡📡📡📡\n\nXataka TV, canal de Youtube del medio líder en tecnología. Te informamos sobre la actualidad de los mejores productos tecnológicos: smartphones, teléfonos móviles y sus apps (Android e iPhone), ordenadores e informática, televisiones y smart tv, tablets, drones, videoconsolas y juegos, cámaras de fotos y fotografía, todos los gadgets que puedas imaginar del mundo tech.\n\nHacemos pruebas de producto que nos permiten hacer los mejores análisis y reviews siempre en español. Compartimos nuestras impresiones con comparativas con competidores. Expresamos nuestra opinión, siempre objetiva, para que estés siempre a la vanguardia de la información.'
    assert episode.image == 'https://yewtu.be/vi/97L58ya1qu8/hqdefault.jpg'
    assert episode.content_type == 'video/mp4'
    assert episode.date.date() == datetime.date(2022, 4, 5)
