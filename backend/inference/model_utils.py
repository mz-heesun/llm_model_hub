from typing import Annotated, Sequence, TypedDict, Dict, Optional,List, Any,TypedDict
from utils.config import DEFAULT_REGION

if DEFAULT_REGION.startswith('cn'):
    from modelscope import  AutoTokenizer
else:
    from transformers import  AutoTokenizer

from logger_config import setup_logger
import logging
logger = setup_logger('serving.py', log_file='deployment.log', level=logging.INFO)

def _get_init_kwargs(model_args) -> Dict[str, Any]:
    r"""
    Gets arguments to load config/tokenizer/model.

    Note: including inplace operation of model_args.
    """
    return {
        "trust_remote_code": True,
        "cache_dir": model_args['cache_dir'],
        "revision": model_args['revision'],
        "token": model_args['token'],
    }



# def patch_tokenizer(tokenizer: "PreTrainedTokenizer") -> None:
#     if "PreTrainedTokenizerBase" not in str(tokenizer._pad.__func__):
#         tokenizer._pad = MethodType(PreTrainedTokenizerBase._pad, tokenizer)
        
def load_tokenizer(model_args):
    r"""
    Loads pretrained tokenizer.

    Note: including inplace operation of model_args.
    """
    init_kwargs = _get_init_kwargs(model_args)
    logger.info(f'init_kwargs:{model_args}')
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            model_args['model_name_or_path'],
            use_fast=False,
            # split_special_tokens=model_args.split_special_tokens,
            padding_side="right",
            **init_kwargs,
        )
    except ValueError:  # try the fast one
        tokenizer = AutoTokenizer.from_pretrained(
            model_args['model_name_or_path'],
            use_fast=True,
            padding_side="right",
            **init_kwargs,
        )

    # if model_args.new_special_tokens is not None:
    #     num_added_tokens = tokenizer.add_special_tokens(
    #         dict(additional_special_tokens=model_args.new_special_tokens),
    #         replace_additional_special_tokens=False,
    #     )
    #     logger.info("Add {} to special tokens.".format(",".join(model_args.new_special_tokens)))
    #     if num_added_tokens > 0 and not model_args.resize_vocab:
    #         model_args.resize_vocab = True
    #         logger.warning("New tokens have been added, changed `resize_vocab` to True.")

    # patch_tokenizer(tokenizer)
    return tokenizer

def apply_default_chat_template(conversation, tokenize=True, add_generation_prompt=False):
    """
    Applies a chat template to a conversation.

    Args:
        conversation (List[Dict]): A list of dictionaries representing the conversation.
            Each dictionary should have 'role' and 'content' keys.
        tokenize (bool, optional): Whether to tokenize the result. Defaults to True.
        add_generation_prompt (bool, optional): Whether to add a generation prompt at the end. Defaults to False.

    Returns:
        Union[str, List[int]]: The formatted conversation as a string or list of token ids.
    """
    result = ""
    for message in conversation:
        role = message['role']
        content = message['content']
        
        if role == 'system':
            result += f"{content}\n\n"
        elif role == 'user':
            result += f"{content}\n\n"
        elif role == 'assistant':
            result += f"{content}\n\n"
        else:
            raise ValueError(f"Unknown role: {role}")
    return result