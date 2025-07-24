from . import atlas, audio, animation, spine ,pack

type_handler_map = {
    "cc.SpriteAtlas": atlas.handle,
    "cc.AudioClip": audio.handle,
    "cc.AnimationClip": animation.handle,
    "sp.SkeletonData": spine.handle,
    "pack": pack.handle
}

def get_handler_for_type(res_type):
    return type_handler_map.get(res_type)