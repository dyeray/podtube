import datetime

from plugins.invidious import PluginImpl


def test_get_feed_channel(utils, monkeypatch, httpx_mock):
    monkeypatch.setenv("INVIDIOUS_DOMAIN", "invidious.namazso.eu")
    channel_id = "UCk195x4zYdMx4LhqEwhcPng"
    expected_url = f"https://invidious.namazso.eu/feed/channel/{channel_id}"
    httpx_mock.add_response(
        method="GET",
        url=expected_url,
        content=utils.get_fixture("invidious_channel.xml"),
        status_code=200,
    )
    expected_episode_id = "dpkt5MmlWZY"

    plugin = PluginImpl({})
    feed = plugin.get_feed(channel_id)
    episode = feed.items[0]
    assert feed.feed_id == channel_id
    assert feed.title == "Instituto de Física Teórica IFT"
    assert feed.description == "Instituto de Física Teórica IFT"
    assert feed.link == f"https://invidious.namazso.eu/channel/{channel_id}"
    assert (
        feed.image
        == "https://yt3.ggpht.com/ytc/AKedOLQ1m7mh1IRDdXuiZ0J2IuVGDAo7EcfkbWewhP4pHA=s900-c-k-c0x00ffffff-no-rj"
    )

    assert episode.item_id == expected_episode_id
    assert (
        episode.title == "¿Por Qué Todo OSCILA en el Universo? | El OSCILADOR ARMÓNICO"
    )
    assert (
        episode.description
        == """<content xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns:media="http://search.yahoo.com/mrss/" type="xhtml">
      <div xmlns="http://www.w3.org/1999/xhtml">
        <a href="https://yewtu.be/watch?v=dpkt5MmlWZY">
          <img src="https://yewtu.be/vi/dpkt5MmlWZY/mqdefault.jpg"/>
        </a>
        <p style="word-break:break-word;white-space:pre-wrap">Desde las cuerdas de un violín hasta el plasma ardiente del universo primitivo, pasando por los campos cuánticos y las ondas gravitacionales, TODO oscila en el universo. Angel Uranga nos explica que detrás de estos patrones se esconde el concepto posiblemente más influyente de la Historia de la Física: el oscilador armónico. 
#Oscilador#Armonico

No te pierdas ningún vídeo: solo tienes que... ¡SUSCRIBIRTE!, ¡es GRATIS!:
https://www.youtube.com/user/IFTMadrid?sub_confirmation=1

¡Síguenos en TWITTER!            https://www.twitter.com/ift_uam_csic
¡INSTAGRAM!                      https://www.instagram.com/ift_madrid/
¡También en FACEBOOK!            https://www.facebook.com/pages/IFT/444787088891187
¡Y consulta nuestra página web!  https://www.ift.uam-csic.es


CRÉDITOS

Galileo
https://www.nuevarevista.net/la-verdad-sobre-el-caso-galileo/

Skate park
X Games
https://www.youtube.com/watch?v=aEAAWlRFcxo

Péndulo humano Walter Levin
https://www.youtube.com/channel/UCiEHVhv0SBMpP75JbzJShqw

Columpio gran amplitud
https://www.youtube.com/watch?v=zGNCEtg-acY

Caída cuerda
https://www.youtube.com/watch?v=4ec12VKWv_E

Reloj
https://www.youtube.com/watch?v=M7s2K1nK7Go
https://www.youtube.com/watch?v=Bs5TziMwwQI

Péndulos desfasados
eclipticom
https://www.youtube.com/watch?v=ihj_tMD_vO4

Bungee Jump al agua
https://www.youtube.com/watch?v=Bm1oBkQBMvk

Figuras Lissajous
https://www.youtube.com/watch?v=uPbzhxYTioM

Acrobacia comba
https://www.youtube.com/watch?v=PUWg7fXnCf0

Animación cuerdas vibrando y columnas de presión
https://ophysics.com/waves6.html

Guitarra, violín
https://www.youtube.com/watch?v=QXjdGBZQvLc

Tambor, platillo
https://www.youtube.com/watch?v=QXjdGBZQvLc

Saxo
https://www.youtube.com/watch?v=SWaQdHoCvYk

Aire y sonido
Audiopedia
https://www.youtube.com/watch?v=bYoTRx6gGX0

Tímpano
https://www.youtube.com/watch?v=eQEaiZ2j9oc

Muelles y campos cuánticos
https://www.ribbonfarm.com/2015/08/20/qft/



Extractos de vídeos de J.L.Crespo para IFT

La Energía Oscura EXPLICADA
https://www.youtube.com/watch?v=ysIQMAjpuYY

La Teoría de Cuerdas en 7 Minutos
https://www.youtube.com/watch?v=yd1jx1DkXb4

¿Qué Pasó ANTES del Big Bang? | Inflación Cósmica
https://www.youtube.com/watch?v=6n2cw_AW01I

Chiken Teriyaki
Rosalía 
Motomami
https://www.youtube.com/watch?v=OG4gq9fCoRE

Ataque a sandía
Kuma Films
https://www.youtube.com/watch?v=WozbZMljRiM

Surf
https://www.youtube.com/watch?v=f6Ltml0uXq4

Vacío QCD
CSSM, Univ. Adelaide, Australia
https://www.youtube.com/watch?v=WZgZI5vymiM

Puente Tacoma
https://www.youtube.com/watch?v=lXyG68_caV4

Columpio
https://www.youtube.com/watch?v=5JbpcsH80us


Sonido Matrix
YouToogle
https://www.youtube.com/watch?v=7M06QVsv3S0

Miniatura
MIKE DUNNING/GETTY
Via Wired
https://www.wired.com/2016/10/modeling-pendulum-harder-think/</p>
      </div>
    </content>"""
    )
    assert episode.image == "https://yewtu.be/vi/dpkt5MmlWZY/mqdefault.jpg"
    assert episode.content_type == "video/mp4"
    assert episode.date.date() == datetime.date(2022, 4, 21)


def test_get_feed_playlist(utils, monkeypatch, httpx_mock):
    monkeypatch.setenv("INVIDIOUS_DOMAIN", "invidious.namazso.eu")
    playlist_id = "PLH3mdhuA3a24qt8c7fgcbknrLqe5Ijia2"
    expected_url = f"https://invidious.namazso.eu/feed/playlist/{playlist_id}"
    httpx_mock.add_response(
        method="GET",
        url=expected_url,
        content=utils.get_fixture("invidious_playlist.xml"),
        status_code=200,
    )
    expected_episode_id = "97L58ya1qu8"

    plugin = PluginImpl({"feed_type": "playlist"})
    feed = plugin.get_feed(playlist_id)
    episode = feed.items[0]
    assert feed.feed_id == playlist_id
    assert feed.title == "Laberinto de papel"
    assert feed.description == "Laberinto de papel"
    assert feed.link == f"https://invidious.namazso.eu/playlist?list={playlist_id}"
    assert feed.image == ""

    assert episode.item_id == expected_episode_id
    assert (
        episode.title
        == "BRUNO PUELLES | Finalista del premio Minotauro por 'SIMBIOSIS'"
    )
    assert (
        episode.description
        == '⭐️⭐️ Suscríbete a nuestro canal https://bit.ly/3iFHitH ⭐️⭐️\n\nHoy hablamos con Bruno Puelles, uno de los finalistas de los Premios Minotauro por su novela de ciencia ficción "Simbiosis". Una novela híbrida entre ciencia ficción y novela negra, que narra la vida de unos personajes en simbiosis con una especie extraterrestre que llega a la Tierra. \n\n#Laberintodepapel #Minotauro #Literatura\n\nEste contenido es una colaboración y patrocinio entre Xataka y la marca, pero no hay pacto sobre el guión ni la selección de los temas. Esta es la manera que tenemos de generar ingresos en el canal\n\n🔋🔋🔋🔋\n\nSuscríbete http://bit.ly/VIpeW9\n\n📹Echa un vistazo a nuestros vídeos https://www.youtube.com/user/XatakaTV...\n📹Sigue de cerca nuestras playlists https://www.youtube.com/user/XatakaTV...\n\n📰 Newsletter: https://www.getrevue.co/profile/xataka\n🕺🏽 Tiktok https://vm.tiktok.com/ZSt7b3aJ/\n👾 Twitch https://www.twitch.tv/elstream \n📱 La Cacharrería https://www.xataka.com/la-cacharreria/search \n📘Facebook https://www.facebook.com/Xataka\n🕊Twitter http://www.twitter.com/xataka\n📸Instagram http://instagram.com/xataka\n💬Telegram https://t.me/xataka\n🖥Leer más: http://www.xataka.com/\n\n📡📡📡📡\n\nXataka TV, canal de Youtube del medio líder en tecnología. Te informamos sobre la actualidad de los mejores productos tecnológicos: smartphones, teléfonos móviles y sus apps (Android e iPhone), ordenadores e informática, televisiones y smart tv, tablets, drones, videoconsolas y juegos, cámaras de fotos y fotografía, todos los gadgets que puedas imaginar del mundo tech.\n\nHacemos pruebas de producto que nos permiten hacer los mejores análisis y reviews siempre en español. Compartimos nuestras impresiones con comparativas con competidores. Expresamos nuestra opinión, siempre objetiva, para que estés siempre a la vanguardia de la información.'
    )
    assert episode.image == "https://yewtu.be/vi/97L58ya1qu8/hqdefault.jpg"
    assert episode.content_type == "video/mp4"
    assert episode.date.date() == datetime.date(2022, 4, 5)
