from . import atlas, texture, audio, animation, spine, spriteframe

type_handler_map = {
    "cc.SpriteAtlas": atlas.handle,
    "cc.Texture2D": texture.handle,
    "cc.AudioClip": audio.handle,
    "cc.AnimationClip": animation.handle,
    "sp.SkeletonData": spine.handle,
    "cc.SpriteFrame": spriteframe.handle,
}

def get_handler_for_type(res_type):
    return type_handler_map.get(res_type)