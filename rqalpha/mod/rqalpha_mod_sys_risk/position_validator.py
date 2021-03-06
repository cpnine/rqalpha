# -*- coding: utf-8 -*-
#
# Copyright 2017 Ricequant, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from rqalpha.interface import AbstractFrontendValidator
from rqalpha.const import SIDE, POSITION_EFFECT, ACCOUNT_TYPE

from rqalpha.utils.i18n import gettext as _


class PositionValidator(AbstractFrontendValidator):
    @staticmethod
    def _stock_validator(account, order):
        if order.side != SIDE.SELL:
            return True

        position = account.positions[order.order_book_id]
        if order.quantity <= position.sellable:
            return True

        order.mark_rejected(_(
            "Order Rejected: not enough stock {order_book_id} to sell, you want to sell {quantity},"
            " sellable {sellable}").format(
            order_book_id=order.order_book_id,
            quantity=order.quantity,
            sellable=position.sellable,
        ))
        return False

    @staticmethod
    def _future_validator(account, order):
        if order.position_effect != POSITION_EFFECT.CLOSE:
            return True

        position = account.positions[order.order_book_id]
        if order.side == SIDE.BUY and order.quantity > position.closable_sell_quantity:
            order.mark_rejected(_(
                "Order Rejected: not enough securities {order_book_id} to buy close, target"
                " sell quantity is {quantity}, sell_closable_quantity {closable}").format(
                order_book_id=order.order_book_id,
                quantity=order.quantity,
                closable=position.closable_sell_quantity,
            ))
            return False
        elif order.side == SIDE.SELL and order.quantity > position.closable_buy_quantity:
            order.mark_rejected(_(
                "Order Rejected: not enough securities {order_book_id} to sell close, target"
                " sell quantity is {quantity}, buy_closable_quantity {closable}").format(
                order_book_id=order.order_book_id,
                quantity=order.quantity,
                closable=position.closable_buy_quantity,
            ))
            return False
        return True

    def can_submit_order(self, account, order):
        if account.type == ACCOUNT_TYPE.STOCK:
            return self._stock_validator(account, order)
        elif account.type == ACCOUNT_TYPE.FUTURE:
            return self._future_validator(account, order)
        else:
            raise NotImplementedError

    def can_cancel_order(self, account, order):
        return True
