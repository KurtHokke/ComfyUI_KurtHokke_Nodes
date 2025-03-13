from ..utils import CATEGORY
import comfy.sd
import folder_paths

class NoModel_CkptLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "ckpt_name": (folder_paths.get_filename_list("checkpoints"), {"tooltip": "The name of the checkpoint (model) to load."}),
            }
        }
    RETURN_TYPES = ("CLIP", "VAE")
    FUNCTION = "load_nomodel_checkpoint"

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.LOADERS.value

    def load_nomodel_checkpoint(self, ckpt_name):
        ckpt_path = folder_paths.get_full_path_or_raise("checkpoints", ckpt_name)
        out = comfy.sd.load_checkpoint_guess_config(ckpt_path, output_vae=True, output_clip=True, embedding_directory=folder_paths.get_folder_paths("embeddings"), output_model=False)
        clip = out[1]
        vae = out[2]
        return (clip, vae)

