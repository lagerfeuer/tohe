import os
import tempfile
from typing import Optional
from subprocess import call


def call_editor(content: Optional[str] = None) -> str:
    EDITOR = os.environ.get('EDITOR')
    if EDITOR is None:
        raise EnvironmentError('No $EDITOR specified!')
    with tempfile.NamedTemporaryFile(prefix='tohe_', suffix='.tmp') as tf:
        if content:
            tf.write(bytes(content, 'utf-8'))
            tf.flush()
        call([EDITOR, tf.name])
        tf.seek(0)
        return tf.read().decode('utf-8')
