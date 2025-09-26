from .prompt import Prompt
__all__ = ["Prompt"]

# keep your guarded prompts facade
try:
    from types import SimpleNamespace
    from ._core import (
        set_base_dir, put, get, get_version, list_all, list_versions,
        meta_version, token, template, render, render_version, jinja_variables,
    )
    prompts = SimpleNamespace(
        save=put, read=get, read_version=get_version, list=list_all,
        versions=list_versions, meta=meta_version, token=token,
        template=template, render=render, render_version=render_version, vars=jinja_variables,
        set_base_dir=set_base_dir,
    )
    __all__.extend(["prompts", "set_base_dir"])

    # expose tenants helpers
    from .tenants import (
        key as tenants_key,
        list_semvers as tenants_list_semvers,
        latest_semver as tenants_latest_semver,
        save as tenants_save,
        read as tenants_read,
        ensure_initial as tenants_ensure_initial,
        read_cached as tenants_read_cached,
    )
    tenants = SimpleNamespace(
        key=tenants_key,
        list_semvers=tenants_list_semvers,
        latest_semver=tenants_latest_semver,
        save=tenants_save,
        read=tenants_read,
        ensure_initial=tenants_ensure_initial,
        read_cached=tenants_read_cached,
    )
    __all__.append("tenants")
except Exception:
    pass
