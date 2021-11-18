from microns_utils import version_utils

__version__ = version_utils.check_package_version(
    package='microns-manual-proofreading', 
    check_if_latest=True, 
    check_if_latest_kwargs=dict(
        owner='cajal', 
        repo='microns-manual-proofreading', 
        source='tag', 
    )
)

def check_latest_version_from_github(owner='cajal', repo='microns-manual-proofreading', source='tag', warn=True):
    """
    Wrapper for :func:`~microns_utils.version_utils.check_latest_version_from_github`
    """
    return version_utils.check_latest_version_from_github(owner=owner, repo=repo, source=source, warn=warn)