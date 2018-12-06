# -*- coding: utf-8 -*-
import re


def get_nums(value):
    """
    通过正则表达式获取 评论数，点赞数和收藏数
    """
    re_match = re.match(".*?(\d+).*", value)
    if re_match:
        nums = (int)(re_match.group(1))
    else:
        nums = 0

    return nums


def get_date(value):
    re_match = re.match("([0-9/]*).*?", value.strip())
    if re_match:
        create_date = re_match.group(1)
    else:
        create_date = ""
    return create_date


def remove_comment_tag(value):
    """
    去掉 tag 中的 “评论” 标签
    """
    if "评论" in value:
        return ""
    else:
        return value


def return_value(value):
    """
    do nothing, 只是为了覆盖 ItemLoader 中的 default_processor
    """
    return value