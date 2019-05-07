
# imports
from __future__ import absolute_import
import os
import json
from maya import cmds

# ==============================================================================
# CONSTANTS
# ==============================================================================

_MANAGER_CACHE_DESTINATION = os.getenv("MGEAR_CACHE_MANAGER_CACHE_DESTINATION")
_MANAGER_MODEL_GROUP = os.getenv("MGEAR_CACHE_MANAGER_MODEL_GROUP")
_MANAGER_PREFERENCE_FILE = "animbits_cache_manager.json"
_MANAGER_PREFERENCE_PATH = "{}/mGear".format(os.getenv("MAYA_APP_DIR"))
_MANAGER_RIG_ATTRIBUTE = os.getenv("MGEAR_CACHE_MANAGER_RIG_ATTRIBUTE")
# ==============================================================================


def get_cache_destination_path():
    """ Returns the cache destination path

    This methods returns a path pointing to where the cache manager will store
    the GPU caches.

    If the **MGEAR_CACHE_MANAGER_CACHE_DESTINATION** environment
    variable has been set it will return whatever path has been set if valid.
    If none has been set or fails to use that path this method tries then
    to return whatever settings has been set on the **cache manager preferences
    file**.

    Finally if no environment variable or preference file is been set then we
    use the **OS TEMP** folder as destination path.
    """

    # if env variable is set
    if (_MANAGER_CACHE_DESTINATION and
            os.path.exists(_MANAGER_CACHE_DESTINATION)):
        return _MANAGER_CACHE_DESTINATION

    # if pref file exists
    if get_preference_file_cache_destination_path():
        return get_preference_file_cache_destination_path()

    # returns temp. folder
    return os.getenv("TMPDIR")


def get_model_group():
    """ Returns the model group name to cache

    This methods returns a string with the name of the transform node to use
    when caching the geometry/model

    If the **MGEAR_CACHE_MANAGER_MODEL_GROUP** environment
    variable has been set it will return the name stored in it.
    If none has been set or fails to use that name this method tries then
    to return whatever settings has been set on the **cache manager preferences
    file**.

    Finally if no environment variable or preference file is been set then we
    fall back to selection.
    """

    pass


def get_preference_file_cache_destination_path():
    """ Returns the folder path set on the preference file

    Returns:
        str or None: The path stored in the preference file or None if invalid
    """

    # preference file
    pref_file = get_preference_file()

    try:
        with open(pref_file, 'r') as file_r:
            # reads json file and get the cache path
            json_dict = json.load(file_r)
            value = json_dict["preferences"][0]["cache_manager_cache_path"]

            if os.path.exists(value):
                return value

            print("Path {} saved on preference file doesn't exist or is "
                  "invalid".format(value))
            return

    except Exception as e:
        message = "Contact mGear's developers reporting this issue to get help"
        print("{} - {} / {}".format(type(e).__name__, e,
                                    message))
        return


def get_preference_file():
    """ Returns the preference file path and name

    Returns:
        str: preference file path and name
    """

    return "{}/{}".format(_MANAGER_PREFERENCE_PATH, _MANAGER_PREFERENCE_FILE)


def get_scene_rigs():
    """ The rigs from current Maya session

    This method search for rigs in your current Maya scene.
    If the MGEAR_CACHE_MANAGER_RIG_ATTRIBUTE has been set it will try to find
    rigs based on the attribute set on the environment variable. Otherwise
    it will use the attribute **gear_version** in order to find rigs in scene.

    Returns:
        list or None: mGear rig top node or None
    """

    if _MANAGER_RIG_ATTRIBUTE:
        try:
            rigs = [x.split(".")[0] for x in cmds.ls(
                "*.{}".format(_MANAGER_RIG_ATTRIBUTE), recursive=True)]
        except RuntimeError:
            raise ValueError("Invalid attribute key: {} - is not a valid "
                             "attribute key to set on the "
                             "MGEAR_CACHE_MANAGER_RIG_ATTRIBUTE variable"
                             .format(_MANAGER_RIG_ATTRIBUTE))
    else:
        rigs = [x.split(".")[0] for x in cmds.ls("*.gear_version",
                                                 recursive=True)]

    return rigs or None


def get_timeline_values():
    """ Returns the min and max keyframe values from the current playback range

    In order to give more freedom to the artist we always evaluate the playback
    range and not the animation range so that artists can choose what range
    to use when creating the GPU cache

    Returns:
        float, float: min and max value
    """

    # get user timeline playback frame range
    _min = cmds.playbackOptions(query=True, minTime=True)
    _max = cmds.playbackOptions(query=True, maxTime=True)

    return _min, _max
