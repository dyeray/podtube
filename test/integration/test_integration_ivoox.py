import datetime

from plugins.ivoox import PluginImpl


def test_get_feed(utils, httpx_mock):
    channel_id = "podcast-podcast-podcast-campamento-krypton_sq_f167429_1"
    expected_url =  f"https://www.ivoox.com/feed_fg_f167429_filtro_1.xml"
    httpx_mock.add_response(
        method="GET",
        url=expected_url,
        status_code=200,
        content=utils.get_fixture("ivoox.xml"),
    )

    plugin = PluginImpl({})
    feed = plugin.get_feed(channel_id)
    episode = feed.items[0]

    assert feed.feed_id == channel_id
    assert feed.link == f"https://www.ivoox.com/{channel_id}.html"
    assert feed.title == "Campamento Krypton"
    assert (
        feed.description
        == "Un podcast donde la cultura pop brilla, burbujea y se alborota. Monográficos y entrevistas sobre cine, cómic, música, empanadillas y Lina Morgan. Organizadores y creadores de la Monstrua de Cine Chungo, también podías escucharnos en Efecto Doppler (Radio 3)"
    )
    assert (
        feed.image == "https://static-1.ivoox.com/canales/8/b/2/b/8b2b10ebe7c3cc33915eee7af9500ae7_XXL.jpg"
    )
    assert len(feed.items) == 199

    assert (
        episode.item_id
        == "68155285"
    )
    assert episode.title == 'CK#209. Nuevos renacentistas (III): De Dolly Parton a Kiko Rivera - Episodio exclusivo para mecenas'
    assert (
        episode.description == """Agradece a este podcast tantas horas de entretenimiento y disfruta de episodios exclusivos como éste. ¡Apóyale en iVoox! Volvemos a repasar cinco personalidades multifacéticas. 

La fijaci&oacute;n por el pron&oacute;stico del tiempo y el amor por la pintura de David Lynch, la peculiar visi&oacute;n de la vida sana de la novia de Iron Man Gwyneth Paltrow, el parque tem&aacute;tico y el alma filantr&oacute;pica de Dolly Parton, el talento musical y la visi&oacute;n empresarial de Shaquille O ' Neal  y, bueno, Kiko Rivera intentando labrarse alg&uacute;n futuro. <a href="https://www.ivoox.com/ck-209-nuevos-renacentistas-iii-de-dolly-parton-a-audios-mp3_rf_68155285_1.html">Escucha el episodio completo</a> en la app de iVoox, o descubre todo el catálogo de <a href="https://www.ivoox.com/originals">iVoox Originals</a> """
    )
    assert episode.date.date() == datetime.date(2025, 3, 11)
    assert (
        episode.image
        == "https://static-2.ivoox.com/audios/3/6/6/5/9801617735663_XXL.jpg"
    )
    assert episode.content_type == "audio/mp4"
