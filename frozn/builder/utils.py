import re

def slugify(value):
    """
    Stolen straight outta Django.  A little dirty right now, needs to be cleaned up
    
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    
    return re.sub('[-\s]+', '-', value)
