#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

class WishlistItem(object):
    def __init__(self,name=None):
        self.name = name

    def can_come_true(self, app=None, context=None):
        raise Exception("a wish's can_come_true function must be specified "
                        "by the implementing wish")

class CashWish(WishlistItem):
    def __init__(self,name=None,ammount=0):
        WishlistItem.__init__(self,name=name)
        self.ammount = ammount

    def can_come_true(self, app=None, context=None):
        return app.data.realm.gold >= self.ammount


class Wishlist(list):
    def __init__(self, app):
        self.app = app

    def pop_wish(self, wish_name, context = None):
        """
        return the next specified wish that can come true, and remove it from
        this list of wishes
        """

        for i in xrange(len(self)):
            wish = self[i]
            if wish != wish_name:
                continue
            answer = wish.can_come_true(self.app, context)
            if not answer:
                continue
            self.pop(i)
            return wish
        return None

    def can_come_true(self, wish_name, context=None):
        """
        Report whether or not a wish can come true
        """

        for i in xrange(len(self)):
            wish = self[i]
            if wish != wish_name:
                continue
            answer = wish.can_come_true(self.app, context)
            if not answer:
                continue
            return True
        return False
