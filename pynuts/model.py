from sqlalchemy.orm import object_mapper
from sqlalchemy.sql import func


class Orderable(object):
    __order_column__ = 'order'

    @property
    def _order_column(self):
        return getattr(self.__class__, self.__order_column__)

    @property
    def _order(self):
        return getattr(self, self.__order_column__)

    def _max_order(self, context):
        return (self.query.session
                .query(func.max(self._order_column))
                .filter(context)
                .scalar())

    def _set_order(self, order):
        return setattr(self, self.__order_column__, order)

    def set_order_to_last(self, context):
        self._set_order(
            self.query.session.query(
                func.coalesce(func.max(self._order_column), 0))
            .filter(context)
            .as_scalar() + 1)

    def reorder(self, context):
        (self.__class__
         .query.filter(self._order_column >= self._order).filter(context)
         .update({self._order_column: self._order_column - 1}))

    def up(self, context):
        self._move('up', context)

    def down(self, context):
        self._move('down', context)

    def _move(self, direction, context):
        """Bust a move"""
        cond = None
        pkey = object_mapper(self).primary_key[0].key

        if direction == 'up':
            if self._order != 1:
                cond = self._order_column == (self._order - 1)
                values = {self._order_column: self._order}
                self._set_order(self._order - 1)

        elif direction == 'down':
            if self._order < self._max_order(context):
                cond = self._order_column == (self._order + 1)
                values = {self._order_column: self._order}
                self._set_order(self._order + 1)
        if cond is not None and values:
            # Flush it now, so that it works
            self.query.session.flush()
            (self.__class__
             .query.filter(cond).filter(context)
             .filter(getattr(self.__class__, pkey) != getattr(self, pkey))
             .update(values))


def reflect(app):
    """ Load all available table definitions from the application database
        and reflect their metadata into the SQLALchemy metadata.
    """
    app.db.metadata.reflect(bind=app.db.get_engine(app))
