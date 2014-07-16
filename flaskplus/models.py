import inflection
from sqlalchemy import text, DDL, event
from sqlalchemy.dialects.postgresql import UUID, ENUM
from flaskplus.extensions import db

Col = db.Column


def get_enum_from_namedtuple(namedtuple_):
    name = inflection.underscore(namedtuple_.__class__.__name__)
    return ENUM(*namedtuple_._fields, name=name)


def get_or_create(session, model_cls, **kwargs):
    """Get or create a model instance from the given kwargs.

    This does not commit a created model instance.
    """
    instance = model_cls.query.filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model_cls(**kwargs)
        session.add(instance)
        return instance


class ModelBase(db.Model):
    """Base model to use for every 'important' model.

    Sets a uuid as the primary field and created/mofified cols at the db level.
    """
    __abstract__ = True

    uuid = Col(UUID, primary_key=True,
               server_default=text("uuid_generate_v4()"))

    created = Col(db.DateTime(timezone=True),
                  server_default=text("TIMEZONE('utc', CURRENT_TIMESTAMP)"))

    modified = Col(db.DateTime(timezone=True),
                   server_default=text("TIMEZONE('utc', CURRENT_TIMESTAMP)"))


@event.listens_for(ModelBase, "instrument_class", propagate=True)
def instrument_class(mapper, class_):
    """This method is called on the instrument_class event that is
    invoked when the superclasses of the ModelBase are inheriting from the
    abstract table.
    """
    if mapper.local_table is not None:
        register_modified_update_trigger(mapper.local_table)


def register_modified_update_trigger(table):
    """Create a trigger on the supplied table name that
    automatically updates the modified field."""
    update_trigger = DDL("""
-- Create the global modified function

CREATE OR REPLACE FUNCTION {func_name}()
    RETURNS trigger AS $$
BEGIN
  NEW.modified := NOW();

  RETURN NEW;
END;
$$ LANGUAGE PLPGSQL;


-- Apply the trigger to the table
CREATE TRIGGER
    {func_name}
BEFORE UPDATE ON
    {tablename}
FOR EACH ROW EXECUTE PROCEDURE
  {func_name}();
        """.format(tablename=table.name, func_name='ModelBase_update_modified'))

    event.listen(table, 'after_create', update_trigger)

