import datetime

from s3p_sdk.plugin.config import (
    PluginConfig,
    CoreConfig,
    TaskConfig,
    trigger,
    MiddlewareConfig,
    modules,
    payload
)
from s3p_sdk.plugin.types import SOURCE
from s3p_sdk.module import (
    WebDriver,
)

config = PluginConfig(
    plugin=CoreConfig(
        reference='pwc',         # уникальное имя источника
        type=SOURCE,                            # Тип источника (SOURCE, ML, PIPELINE)
        files=['pwc.py', ],        # Список файлов, которые будут использоваться в плагине (эти файлы будут сохраняться в платформе)
        is_localstorage=False
    ),
    task=TaskConfig(
        trigger=trigger.TriggerConfig(
            type=trigger.SCHEDULE,
            interval=datetime.timedelta(days=1),    # Интервал перезапуска плагина
        )
    ),
    middleware=MiddlewareConfig(
        modules=[
            modules.TimezoneSafeControlConfig(order=1, is_critical=True),
            modules.FilterOnlyNewDocumentWithDB(order=2, is_critical=True),
            modules.SaveDocument(order=3, is_critical=True),
        ],
        bus=None,
    ),
    payload=payload.PayloadConfig(
        file='pwc.py',                 # python файл плагина (точка входа). Этот файл должен быть указан в `plugin.files[*]`
        classname='PWC',               # имя python класса в указанном файле
        entry=payload.entry.EntryConfig(
            method='content',
            params=[
                payload.entry.ModuleParamConfig(key='web_driver', module_name=WebDriver, bus=True),
                payload.entry.ConstParamConfig(key='max_count_documents', value=50),
                # payload.entry.ConstParamConfig(key='url',
                #                                value='url to the source page'),
            ]
        )
    )
)

__all__ = ['config']
