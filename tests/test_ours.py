from unittest.mock import mock_open, patch

from ours import OursService


def test_one_user_many_affiliate_referers_checkout_and_ours_before_theirs1():
    read_data = """{"client_id":"user15","User-Agent":"Firefox59","document.location":"https://shop.com/products/?id=2","document.referer":"https://yandex.ru/search/?q=купить+котика","date":"2018-04-03T07:59:13.286000Z"}
{"client_id":"user15","User-Agent":"Firefox59","document.location":"https://shop.com/products/id?=2","document.referer":"https://referal.ours.com/?ref=123hexcode","date":"2018-04-04T08:30:14.104000Z"}
{"client_id":"user15","User-Agent":"Firefox59","document.location":"https://shop.com/products/id?=2","document.referer":"https://ad.theirs1.com/?src=q1w2e3r4","date":"2018-04-04T08:45:14.384000Z"}
{"client_id":"user15","User-Agent":"Firefox59","document.location":"https://shop.com/checkout","document.referer":"https://shop.com/products/id?=2","date":"2018-04-04T08:59:16.222000Z"}
"""
    with patch("ours.open", mock_open(read_data=read_data)):
        ours = OursService("path")
        result = ours.process_log()
        assert not result


def test_one_user_many_affiliate_referers_checkout_and_ours_last():
    read_data = """{"client_id":"user15","User-Agent":"Firefox59","document.location":"https://shop.com/products/?id=2","document.referer":"https://yandex.ru/search/?q=купить+котика","date":"2018-04-03T07:59:13.286000Z"}
{"client_id":"user15","User-Agent":"Firefox59","document.location":"https://shop.com/products/id?=2","document.referer":"https://ad.theirs1.com/?src=q1w2e3r4","date":"2018-04-04T08:30:14.384000Z"}
{"client_id":"user15","User-Agent":"Firefox59","document.location":"https://shop.com/products/id?=2","document.referer":"https://referal.ours.com/?ref=123hexcode","date":"2018-04-04T08:45:14.104000Z"}
{"client_id":"user15","User-Agent":"Firefox59","document.location":"https://shop.com/checkout","document.referer":"https://shop.com/products/id?=2","date":"2018-04-04T08:59:16.222000Z"}
"""
    with patch("ours.open", mock_open(read_data=read_data)):
        ours = OursService("path")
        result = ours.process_log()
        assert len(result) == 1
        assert result[0][0] == "https://referal.ours.com/?ref=123hexcode"
        assert result[0][1] == 1


def test_one_user_checkout_and_no_affiliate_referers():
    read_data = """{"client_id":"user15","User-Agent":"Firefox59","document.location":"https://shop.com/products/?id=2","document.referer":"https://yandex.ru/search/?q=купить+котика","date":"2018-04-03T07:59:13.286000Z"}
{"client_id":"user15","User-Agent":"Firefox59","document.location":"https://shop.com/products/?id=2","document.referer":"https://google.com/search/?q=купить+слона","date":"2018-04-03T07:59:23.286000Z"}
{"client_id":"user15","User-Agent":"Firefox59","document.location":"https://shop.com/checkout","document.referer":"https://shop.com/products/id?=2","date":"2018-04-04T08:59:16.222000Z"}
"""
    with patch("ours.open", mock_open(read_data=read_data)):
        ours = OursService("path")
        result = ours.process_log()
        assert not result


def test_one_user_from_ours_then_walking_on_site_then_checkout():
    read_data = """{"client_id":"user15","User-Agent":"Firefox59","document.location":"https://shop.com/products/?id=2","document.referer":"https://referal.ours.com/?ref=123hexcode","date":"2018-04-03T07:59:13.286000Z"}
{"client_id":"user15","User-Agent":"Firefox59","document.location":"https://shop.com/products/id?=3","document.referer":"https://shop.com/products/id?=2","date":"2018-04-04T08:30:14.384000Z"}
{"client_id":"user15","User-Agent":"Firefox59","document.location":"https://shop.com/products/id?=4","document.referer":"https://shop.com/products/id?=3","date":"2018-04-04T08:45:14.104000Z"}
{"client_id":"user15","User-Agent":"Firefox59","document.location":"https://shop.com/checkout","document.referer":"https://shop.com/products/id?=4","date":"2018-04-04T08:59:16.222000Z"}
"""
    with patch("ours.open", mock_open(read_data=read_data)):
        ours = OursService("path")
        result = ours.process_log()
        assert len(result) == 1
        assert result[0][0] == "https://referal.ours.com/?ref=123hexcode"
        assert result[0][1] == 1


def test_one_user_from_ours_buy_two_products():
    read_data = """{"client_id":"user15","User-Agent":"Firefox59","document.location":"https://shop.com/products/?id=2","document.referer":"https://referal.ours.com/?ref=123hexcode","date":"2018-04-03T07:59:13.286000Z"}
{"client_id":"user15","User-Agent":"Firefox59","document.location":"https://shop.com/checkout","document.referer":"https://shop.com/products/id?=2","date":"2018-04-04T08:30:14.384000Z"}
{"client_id":"user15","User-Agent":"Firefox59","document.location":"https://shop.com/products/id?=3","document.referer":"https://shop.com/checkout","date":"2018-04-04T08:45:14.104000Z"}
{"client_id":"user15","User-Agent":"Firefox59","document.location":"https://shop.com/checkout","document.referer":"https://shop.com/products/id?=3","date":"2018-04-04T08:59:16.222000Z"}
"""
    with patch("ours.open", mock_open(read_data=read_data)):
        ours = OursService("path")
        result = ours.process_log()
        assert len(result) == 1
        assert result[0][0] == "https://referal.ours.com/?ref=123hexcode"
        assert result[0][1] == 2


def test_user1_from_ours_user2_from_theirs1_user1_checkout():
    read_data = """{"client_id":"user1","User-Agent":"Firefox59","document.location":"https://shop.com/products/?id=2","document.referer":"https://referal.ours.com/?ref=123hexcode","date":"2018-04-03T07:59:13.286000Z"}
{"client_id":"user2","User-Agent":"Firefox59","document.location":"https://shop.com/products/id?=3","document.referer":"https://ad.theirs1.com/?src=q1w2e3r4","date":"2018-04-04T08:30:14.384000Z"}
{"client_id":"user1","User-Agent":"Firefox59","document.location":"https://shop.com/checkout","document.referer":"https://shop.com/products/id?=2","date":"2018-04-04T08:45:14.104000Z"}
"""
    with patch("ours.open", mock_open(read_data=read_data)):
        ours = OursService("path")
        result = ours.process_log()
        assert len(result) == 1
        assert result[0][0] == "https://referal.ours.com/?ref=123hexcode"
        assert result[0][1] == 1
