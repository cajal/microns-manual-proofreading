from microns_utils import version_utils

__version__ = version_utils.get_package_version(
    package='microns-manual-proofreading', 
    check_if_latest=True, 
    check_if_latest_kwargs=dict(
        owner='cajal', 
        repo='microns-manual-proofreading', 
        source='tag', 
    )
)