"""Model-related helpers for Pynuts."""

from sqlalchemy.orm import object_mapper
from sqlalchemy.sql import func


class Orderable(object):
    """Mix-in class used for ordered tables."""

    #: Name of the column used to sort table lines
    __order_column__ = 'order'

    @property
    def _order_column(self):
        """SQLAlchemy column used to order lines."""
        return getattr(self.__class__, self.__order_column__)

    @property
    def _order(self):
        """Rank of the line."""
        return getattr(self, self.__order_column__)

    def _max_order(self, context):
        """Get rank of the latest line."""
        return (self.query.session
                .query(func.max(self._order_column))
                .filter(context)
                .scalar())

    def _set_order(self, order):
        """Set order of the line."""
        return setattr(self, self.__order_column__, order)

    def set_order_to_last(self, context):
        """Set order of the line to maximum rank + 1."""
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
        """Swap a line with its previous line."""
        self._move('up', context)

    def down(self, context):
        """Swap a line with its next line."""
        self._move('down', context)

    def _move(self, direction, context):
        """Swap a line with another line.

        If ``direction`` is ``'up'``, swap with the previous line.
        If ``direction`` is ``'down'``, swap with the next line.

        """
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
    """Reflect metadata of ``app``'s tables.

    Load all available table definitions from the application database
    and reflect their metadata into the SQLALchemy metadata.

    """
    app.db.metadata.reflect(bind=app.db.get_engine(app))
