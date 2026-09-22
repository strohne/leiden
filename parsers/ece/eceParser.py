#!/usr/bin/env python3

#######################################################################
#
# SYMBOLS SECTION - Can be edited. Changes will be preserved.
#
#######################################################################


import collections
from functools import partial
import os
import sys
from typing import Tuple, List, Set, Union, Any, Optional, Callable, cast

try:
    scriptdir = os.path.dirname(os.path.realpath(__file__))
except NameError:
    scriptdir = ''
if scriptdir and scriptdir not in sys.path: sys.path.append(scriptdir)

try:
    from DHParser import versionnumber
except (ImportError, ModuleNotFoundError):
    i = scriptdir.rfind("/DHParser/")
    if i >= 0:
        dhparserdir = scriptdir[:i + 10]  # 10 = len("/DHParser/")
        if dhparserdir not in sys.path:  sys.path.insert(0, dhparserdir)

from DHParser.compile import Compiler, compile_source, Junction, full_compile
from DHParser.configuration import set_config_value, add_config_values, get_config_value, \
    access_thread_locals, access_presets, finalize_presets, set_preset_value, \
    get_preset_value, read_local_config, CONFIG_PRESET, NEVER_MATCH_PATTERN, ALLOWED_PRESET_VALUES
from DHParser import dsl
from DHParser.dsl import recompile_grammar
from DHParser.ebnf import grammar_changed
from DHParser.error import ErrorCode, Error, canonical_error_strings, has_errors, NOTICE, \
    WARNING, ERROR, FATAL
from DHParser.log import start_logging, suspend_logging, resume_logging
from DHParser.nodetree import Node, WHITESPACE_PTYPE, TOKEN_PTYPE, RootNode, Path, ZOMBIE_TAG
from DHParser.parse import Grammar, PreprocessorToken, Whitespace, Drop, DropFrom, AnyChar, Parser, \
    Lookbehind, Lookahead, Alternative, Pop, Text, Synonym, Counted, Interleave, INFINITE, ERR, \
    Option, NegativeLookbehind, OneOrMore, RegExp, SmartRE, Retrieve, Series, Capture, TreeReduction, \
    ZeroOrMore, Forward, NegativeLookahead, Required, CombinedParser, Custom, IgnoreCase, \
    LateBindingUnary, mixin_comment, last_value, matching_bracket, optional_last_value, \
    PARSER_PLACEHOLDER, RX_NEVER_MATCH, UninitializedError
from DHParser.pipeline import end_points, full_pipeline, create_parser_junction, \
    create_preprocess_junction, create_junction, PseudoJunction, PipelineResult
from DHParser.preprocess import nil_preprocessor, PreprocessorFunc, PreprocessorResult, \
    gen_find_include_func, preprocess_includes, make_preprocessor, chain_preprocessors
from DHParser.stringview import StringView
from DHParser.toolkit import is_filename, load_if_file, cpu_count, \
    ThreadLocalSingletonFactory, expand_table, static, CancelQuery, re
from DHParser.trace import set_tracer, resume_notices_on, trace_history
from DHParser.transform import is_empty, remove_if, TransformationDict, TransformerFunc, \
    transformation_factory, remove_children_if, move_fringes, normalize_whitespace, \
    is_anonymous, name_matches, reduce_single_child, replace_by_single_child, replace_or_reduce, \
    remove_whitespace, replace_by_children, remove_empty, remove_tokens, flatten, all_of, \
    any_of, transformer, merge_adjacent, collapse, collapse_children_if, transform_result, \
    remove_children, remove_content, remove_brackets, change_name, remove_anonymous_tokens, \
    keep_children, is_one_of, not_one_of, content_matches, apply_if, peek, \
    remove_anonymous_empty, keep_nodes, traverse_locally, strip, lstrip, rstrip, \
    replace_content_with, forbid, assert_content, remove_infix_operator, add_error, error_on, \
    left_associative, lean_left, node_maker, has_descendant, neg, has_ancestor, insert, \
    positions_of, replace_child_names, add_attributes, delimit_children, merge_connected, \
    has_attr, has_parent, has_children, has_child, apply_unless, apply_ifelse, traverse
from DHParser import parse as parse_namespace__

import DHParser.versionnumber
if DHParser.versionnumber.__version_info__ < (1, 9, 4):
    print(f'DHParser version {DHParser.versionnumber.__version__} is lower than the DHParser '
          f'version 1.9.4, {os.path.basename(__file__)} has first been generated with. '
          f'Please install a more recent version of DHParser to avoid unexpected errors!')

if sys.version_info >= (3, 14, 0):
    CONFIG_PRESET['multicore_pool'] = 'InterpreterPool'
read_local_config(os.path.join(scriptdir, 'eceConfig.ini'))


#######################################################################
#
# PREPROCESSOR SECTION - Can be edited. Changes will be preserved.
#
#######################################################################



# To capture includes, replace the NEVER_MATCH_PATTERN
# by a pattern with group "name" here, e.g. r'\input{(?P<name>.*)}'
RE_INCLUDE = NEVER_MATCH_PATTERN
RE_COMMENT = NEVER_MATCH_PATTERN  # THIS MUST ALWAYS BE THE SAME AS eceGrammar.COMMENT__ !!!


def eceTokenizer(original_text) -> Tuple[str, List[Error]]:
    # Here, a function body can be filled in that adds preprocessor tokens
    # to the source code and returns the modified source.
    return original_text, []

preprocessing: PseudoJunction = create_preprocess_junction(
    eceTokenizer, RE_INCLUDE, RE_COMMENT)


#######################################################################
#
# PARSER SECTION - Don't edit! CHANGES WILL BE OVERWRITTEN!
#
#######################################################################

class eceGrammar(Grammar):
    r"""Parser for an ece document.

    Instantiate this class and then call the instance with the source
    code as the single argument in order to use the parser, e.g.:
        parser = ece()
        syntax_tree = parser(source_code)
    """
    brackets = Forward()
    supable = Forward()
    unc = Forward()
    source_hash__ = "406577bc6c527e1ebe7c5846609af039"
    early_tree_reduction__ = CombinedParser.MERGE_LEAVES
    disposable__ = re.compile('(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:(?:multiline$))|(?:singleline$))|(?:linestart$))|(?:linebreak$))|(?:lb_sep$))|(?:EOF$))|(?:inscription$))|(?:inline$))|(?:characters$))|(?:letters_range$))|(?:letters_sequence$))|(?:combining$))|(?:combining_diacrytic$))|(?:letter$))|(?:letter_simple$))|(?:letter_plain$))|(?:letter_greek$))|(?:letter_extended$))|(?:letter_apostrophe$))|(?:letter_diacrytic$))|(?:uncable$))|(?:uncertain_combined$))|(?:uncertain_precomposed$))|(?:uncertain_binder$))|(?:uncertain_pc$))|(?:uncertain_am$))|(?:dotbelow$))|(?:combining_dotbelow$))|(?:sups_number$))|(?:sups_letter$))|(?:barable$))|(?:bar_simple$))|(?:bar_combined$))|(?:combining_barabove$))|(?:combining_barbetween$))|(?:barcomposed$))|(?:uncbar$))|(?:combining_barbelow$))|(?:ligable$))|(?:combining_breve$))|(?:supable$))|(?:combining_superscript$))|(?:binder_equal$))|(?:binder_hyphen$))|(?:combining_strikedouble$))|(?:combining_strikethrough$))|(?:combining_strikesolidus$))|(?:brackets$))|(?:spaceseq$))|(?:lost$))|(?:backtick$))|(?:tick$))|(?:prettyspace$)')
    static_analysis_pending__ = []  # type: List[bool]
    parser_initialization__ = ["upon instantiation"]
    COMMENT__ = r''
    comment_rx__ = RX_NEVER_MATCH
    WHITESPACE__ = r'[  ]*'
    WSP_RE__ = mixin_comment(whitespace=WHITESPACE__, comment=COMMENT__)
    wsp__ = Whitespace(WSP_RE__)
    dwsp__ = Drop(Whitespace(WSP_RE__))
    prettyspace = Drop(RegExp('[ ]*'))
    inspace = Series(RegExp('[ \\u00A0]'), dwsp__)
    tick = Drop(Text("´"))
    backtick = Drop(Text("`"))
    letter_extended = RegExp('[àèìòùÀÈÌÒÙáéíóúýÁÉÍÓÚÝâêȇîôûÂÊÎÔÛãñõÃÑÕäëïöüÿÄËÏÖÜŸçÇßØøÅåÆæŒœİḢṪȧėṗṡḣȮŁłↃÞþ]')
    combining_breve = Drop(RegExp('\\u0361'))
    combining_barbelow = Drop(RegExp('[\\u0331\\u0332]'))
    combining_barabove = Drop(RegExp('[\\u0304\\u0305]'))
    ex_unknown = Series(Drop(Text("(")), Text("---"), Drop(Text(")")))
    combining_barbetween = Drop(RegExp('[\\u035E\\uFE26]'))
    lb_sep = Drop(RegExp('\\)'))
    combining_dotbelow = RegExp('\\u0323')
    lb = RegExp('[a-zA-Z]+')
    lost_number = Series(Drop(Text(".c")), RegExp('[0-9]+'), Drop(Text(".")))
    lost_dots = OneOrMore(Text("."))
    lost_unknown = Alternative(Drop(Text(".?.")), Drop(Text("-?-")))
    lost = Alternative(lost_unknown, lost_number, lost_dots)
    gap = Series(Drop(Text("[")), lost, Drop(Text("]")))
    space = Series(Drop(Text("(")), OneOrMore(Text("-")), Drop(Text(")")))
    spaceseq = Series(inspace, space)
    lb_break = RegExp('[\\r\\n]+')
    combining_strikesolidus = Drop(RegExp('[\\u0337]'))
    letter_plain = RegExp('[A-Za-z0-9]')
    combining_strikethrough = Drop(RegExp('[\\u0336]'))
    letter_greek = RegExp('[Α-Ωα-ω]')
    combining_strikedouble = Drop(RegExp('[\\u033F]'))
    letter_apostrophe = RegExp("[']")
    letter_simple = Alternative(letter_plain, letter_greek, letter_extended, letter_apostrophe)
    am = RegExp('[⁊ꝰꝐꝑ’&ꝪꝫŁ»6♃’]')
    binder_hyphen = RegExp('(?<!-)-(?!-)')
    binder_equal = Text("=")
    binder = Alternative(binder_equal, binder_hyphen)
    terminator = RegExp('(?<!\\s)[\\.:,;]')
    combining_superscript = RegExp('[\\u0363-\\u036F]')
    com = Series(supable, combining_superscript)
    linebreak = Series(lb_break, lb, lb_sep, prettyspace)
    combining_diacrytic = RegExp('[\\u0307\\u0308\\u0313]')
    letter_diacrytic = Series(letter_simple, combining_diacrytic)
    letter = Alternative(letter_diacrytic, letter_simple)
    letter_mixed = Synonym(letter)
    uncable = Alternative(com, letter_mixed)
    combining = Alternative(combining_diacrytic, combining_dotbelow, combining_superscript, combining_barabove, combining_barbetween, combining_barbelow, combining_breve, combining_strikethrough, combining_strikesolidus, combining_strikedouble)
    strike_solidus = Series(letter, combining_strikesolidus)
    strike_through = Series(letter, combining_strikethrough)
    letters_sequence = OneOrMore(Series(letter, NegativeLookahead(combining)))
    strike_double = Series(letter, combining_strikedouble)
    strike = Alternative(strike_through, strike_solidus, strike_double)
    letters_range = Series(letters_sequence, Text("-"), letters_sequence)
    barcomposed = RegExp('[ĀĪōīā]')
    letters = Alternative(letters_range, letters_sequence)
    uncbar = Series(unc, combining_barabove)
    barletlig = Series(letter, combining_barbetween, letter, combining_breve, letter)
    ligletbar = Series(letter, combining_breve, letter, combining_barbetween, letter)
    barlig = Series(letter, combining_barbetween, combining_breve, letter)
    ligbar = Series(letter, combining_breve, combining_barbetween, letter)
    sups_letter = RegExp('[ᴬᵃᴮᶜᴰᵈᴱᵉᴳᴴᴵⁱᴶᴷᴸᴹᵐⁿᴺᴼᵒᴾᴿʳˢᵀᵗᵁᵘᵛⱽʷˣʸᶻ]')
    sups_number = RegExp('[⁰¹²³⁴⁵⁶⁷⁸⁹]')
    sup = OneOrMore(Alternative(sups_number, sups_letter))
    sep_word_special = RegExp('[ͦ°ↀꝚ⁜✶☓§‡†✝+◦✢〇⊙⬦◇⋮⦂≡ᛁᛟ᪥⨯ͮ≗᪥◆●𛲜⁘◎△⁙⦚|/⌃!?–]')
    sep_word_punct = RegExp('[:;,]')
    sep_word_period = RegExp('\\.(?!\\?)')
    sep_word_dot = RegExp('[ᣟ·∙⋅]')
    pc = Alternative(sep_word_dot, sep_word_period, sep_word_punct, sep_word_special)
    characters = Alternative(linebreak, am, letters, terminator, binder, pc, inspace)
    dotbelow = Drop(RegExp(' ?(\\u0323)'))
    uncertain_am = Series(am, dotbelow)
    uncertain_pc = Series(pc, dotbelow)
    uncertain_binder = Series(binder, dotbelow)
    uncertain_precomposed = RegExp('[ẠḄḌẸḤỊḲḶṂṆỌṚṢṬỤṾẈỴẒạḅḍẹḥịḳḷṃṇọṛṣṭụṿẉỵẓ]')
    uncertain_combined = Series(uncable, combining_dotbelow)
    linestart = Series(lb, lb_sep, prettyspace)
    nl = Series(RegExp('[\\r\\n]+'), NegativeLookahead(linestart))
    barable = Alternative(pc, am, letter_mixed)
    bar_simple = Alternative(Series(barable, combining_barabove), barcomposed)
    subbar = OneOrMore(Series(letter, combining_barbelow))
    barunc = Series(bar_simple, combining_dotbelow)
    ligable = Alternative(bar_simple, unc, am, strike, pc, com, letter_mixed)
    lig = Series(ligable, OneOrMore(Series(combining_breve, ligable)))
    bar_combined = Series(barable, OneOrMore(Series(combining_barbetween, barable)))
    bar = Alternative(ligletbar, barletlig, ligbar, barlig, barunc, uncbar, Series(bar_simple, NegativeLookahead(combining_breve)), bar_combined)
    inline = Alternative(subbar, bar, lig, unc, sup, com, strike, spaceseq, characters, nl)
    add = Series(backtick, OneOrMore(Alternative(inline, brackets)), tick)
    era = Series(Drop(Text("〚")), OneOrMore(Alternative(inline, brackets)), Drop(Text("〛")))
    cpl = Series(Drop(Text("[")), OneOrMore(Alternative(inline, brackets)), Drop(Text("]")))
    res = Series(Drop(Text("[[")), OneOrMore(Alternative(inline, brackets)), Drop(Text("]]")))
    ex_tentative = Series(Drop(Text("(")), OneOrMore(inline), Drop(Text("?")), Drop(Text(")")))
    ex_known = Series(Drop(Text("(")), OneOrMore(inline), Drop(Text(")")))
    ex = Alternative(ex_known, ex_unknown, ex_tentative)
    dec = Series(Drop(Text("((")), OneOrMore(inline), Drop(Text("))")))
    EOF = Drop(NegativeLookahead(RegExp('.')))
    inscription = OneOrMore(Alternative(inline, brackets, nl))
    singleline = Series(inscription, EOF, mandatory=1)
    multiline = Series(linestart, inscription, EOF, mandatory=2)
    brackets.set(Alternative(dec, spaceseq, ex, gap, res, cpl, era, add))
    supable.set(Alternative(unc, pc, letter))
    unc.set(Alternative(uncertain_combined, uncertain_precomposed, uncertain_binder, uncertain_pc, uncertain_am))
    lines = Alternative(multiline, singleline)
    root__ = lines
    
parsing: PseudoJunction = create_parser_junction(eceGrammar)
get_grammar = parsing.factory  # for backwards compatibility, only


try:
    assert RE_INCLUDE == NEVER_MATCH_PATTERN or \
        RE_COMMENT in (eceGrammar.COMMENT__, NEVER_MATCH_PATTERN), \
        "Please adjust the pre-processor-variable RE_COMMENT in file eceParser.py so that " \
        "it either is the NEVER_MATCH_PATTERN or has the same value as the COMMENT__-attribute " \
        "of the grammar class eceGrammar! " \
        'Currently, RE_COMMENT reads "%s" while COMMENT__ is "%s". ' \
        % (RE_COMMENT, eceGrammar.COMMENT__) + \
        "\n\nIf RE_COMMENT == NEVER_MATCH_PATTERN then includes will deliberately be " \
        "processed, otherwise RE_COMMENT==eceGrammar.COMMENT__ allows the " \
        "preprocessor to ignore comments."
except (AttributeError, NameError):
    pass



#######################################################################
#
# AST SECTION - Can be edited. Changes will be preserved.
#
#######################################################################

@transformation_factory(str)
def move_name_to_attr(path: Path, attrName: str):
    node = path[-1]
    node.attr[attrName] = node.name.rsplit('_', 1)[-1]

@transformation_factory(str)
def move_content_to_attr(path: Path, attrName :str):
    node = path[-1]
    assert not node.children
    node.attr[attrName] =  node.content
    node.result = ''

def clear_content(path: Path):
    node = path[-1]
    node.result = ''

@transformation_factory(str)
def count_characters(path: Path, attrName : str):
    node = path[-1]
    assert not node.children
    node.attr[attrName] = len(node.content)
    node.result = ''

def remove_dot_below(path: Path):
    currentNode = path[-1]
    nodes = list(currentNode.children) + [currentNode]

    for node in nodes:
        plain = node.content
        if plain != "":

            # Translate precomposed characters
            translate_from = "ẠḄḌẸḤỊḲḶṂṆỌṚṢṬỤṾẈỴẒạḅḍẹḥịḳḷṃṇọṛṣṭụṿẉỵẓ"
            translate_to   = "ABDEHIKLMNORSTUVWYZabdehiklmnorstuvwyz"
            plain = plain.translate(str.maketrans(translate_from, translate_to))

            # Remove combined dot
            plain = plain.replace(u"\u0323","")
            node.result = plain

def remove_bars(path: Path):
    currentNode = path[-1]
    nodes = list(currentNode.children) + [currentNode]

    for node in nodes:
        plain = node.content
        if plain != "":

            # Translate precomposed characters
            translate_from = "ꝑĀōīā"
            translate_to   = "pAoia"
            plain = plain.translate(str.maketrans(translate_from, translate_to))

            node.result = plain

def replace_sup(path: Path):
    currentNode = path[-1]

    nodes = list(currentNode.children) + [currentNode]

    for node in nodes:
        plain = node.content
        if plain != "":

            # Translate precomposed characters
            translate_from = "⁰¹²³⁴⁵⁶⁷⁸⁹ᴬͣᴮᶜᴰᵈᴱͤᴳᴴᴵͥᴶᴷᴸᴹᴺᴼᴾᴿͬˢᵀͭᵁⱽᵛʷˣʸᶻⁱⁱ"
            translate_to   = "0123456789AaBCDdEeGHIiJKLMNOPRrsTtUVvwxyzii"
            plain = plain.translate(str.maketrans(translate_from, translate_to))

            node.result = plain


ece_AST_transformation_table = {
    # AST Transformations for the ece-grammar
    # Special rules:
    # "<<<": [],  # called once before the tree-traversal starts
    # ">>>": [],  # called once after the tree-traversal has finished
    # "<": [],  # called for each node before calling its specific rules
    # "*": [],  # fallback for nodes that do not appear in this table
    # ">": [],   # called for each node after calling its specific rules

    #"singlepart": [change_name("part")],

    "lb": [move_content_to_attr("n")],
    "nl": [clear_content],
    "lb_break": [clear_content, change_name("nl")],

    "pc": [replace_by_single_child, move_content_to_attr("rend"), move_name_to_attr("type"), change_name("pc")],
    "am": [move_content_to_attr("rend")],
    "space": [count_characters("extent")],
    "ex": [replace_by_single_child, move_name_to_attr("type"), change_name("ex")],
    "strike": [replace_by_single_child, move_name_to_attr("type"), change_name("strike")],

    "lost_unknown": [change_name("gap"), replace_by_single_child, clear_content],
    "lost_number":  [change_name("gap"), replace_by_single_child, move_content_to_attr("quantity")],
    "lost_dots":    [change_name("gap"), replace_by_single_child, count_characters("quantity")],

    "gap": [change_name("gap"), replace_by_single_child],
    "gap_nested": [change_name("gap"), replace_by_single_child],

    "subbar": [remove_bars],
    #"bar": [remove_bars],

    "ligbar" : [move_name_to_attr("type"), change_name("lig")],
    "barlig" : [move_name_to_attr("type"), change_name("lig")],
    "ligletbar" : [move_name_to_attr("type"), change_name("lig")],
    "barletlig" : [move_name_to_attr("type"), change_name("lig")],

    "barunc" : [change_name("unc")],

    "unc": [remove_dot_below],
    "sup":   [replace_sup],

    "letter_mixed": [change_name("letters")]

}


# DEPRECATED, because it requires pickling the transformation-table, which rules out lambdas!
# ASTTransformation: Junction = create_junction(
#     ece_AST_transformation_table, "CST", "AST", "transtable")

def eceTransformer() -> TransformerFunc:
    return static(partial(
        transformer, 
        transformation_table=ece_AST_transformation_table.copy(),
        src_stage='CST', 
        dst_stage='AST'))

ASTTransformation: Junction = Junction(
    'CST', ThreadLocalSingletonFactory(eceTransformer), 'AST')
get_transformer = ASTTransformation.factory  # for backwards compatibility, only


#######################################################################
#
# COMPILER SECTION - Can be edited. Changes will be preserved.
#
#######################################################################

class eceCompiler(Compiler):
    """Compiler for the abstract-syntax-tree of a 
        ece source file.
    """

    def __init__(self):
        super(eceCompiler, self).__init__()
        self.forbid_returning_None = True  # set to False if any compilation-method is allowed to return None

    def reset(self):
        super().reset()
        # initialize your variables here, not in the constructor!

    def prepare(self, root: RootNode) -> None:
        assert root.stage == "AST", f"Source stage `AST` expected, `but `{root.stage}` found."
        root.stage = "ece"
    def finalize(self, result: Any) -> Any:
        return result

    def on_sco(self, node):
        return self.fallback_compiler(node)

    # def on_sec(self, node):
    #     return node

    # def on_snr(self, node):
    #     return node

    # def on_snt(self, node):
    #     return node

    # def on_b(self, node):
    #     return node

    # def on_par(self, node):
    #     return node

    # def on_lno(self, node):
    #     return node

    # def on_lin(self, node):
    #     return node

    # def on_cnt(self, node):
    #     return node

    # def on_table(self, node):
    #     return node

    # def on_row(self, node):
    #     return node

    # def on_cell(self, node):
    #     return node

    # def on_entry(self, node):
    #     return node

    # def on_inscription(self, node):
    #     return node

    # def on_inline(self, node):
    #     return node

    # def on_tags(self, node):
    #     return node

    # def on_app(self, node):
    #     return node

    # def on_appalpha(self, node):
    #     return node

    # def on_appnum(self, node):
    #     return node

    # def on_app_id(self, node):
    #     return node

    # def on_app_nr(self, node):
    #     return node

    # def on_all(self, node):
    #     return node

    # def on_em(self, node):
    #     return node

    # def on_chr(self, node):
    #     return node

    # def on_sup(self, node):
    #     return node

    # def on_sub(self, node):
    #     return node

    # def on_nl(self, node):
    #     return node

    # def on_insec(self, node):
    #     return node

    # def on_insec_combined_plain(self, node):
    #     return node

    # def on_insec_combined_extended(self, node):
    #     return node

    # def on_insec_precomposed(self, node):
    #     return node

    # def on_insec_binder(self, node):
    #     return node

    # def on_insec_separator(self, node):
    #     return node

    # def on_letters(self, node):
    #     return node

    # def on_letters_sequence(self, node):
    #     return node

    # def on_letters_range(self, node):
    #     return node

    # def on_letters_plain(self, node):
    #     return node

    # def on_letters_extended(self, node):
    #     return node

    # def on_letters_diacrytic(self, node):
    #     return node

    # def on_letters_cross(self, node):
    #     return node

    # def on_letters_apostrophe(self, node):
    #     return node

    # def on_terminator(self, node):
    #     return node

    # def on_binder(self, node):
    #     return node

    # def on_binder_equal(self, node):
    #     return node

    # def on_binder_hyphen(self, node):
    #     return node

    # def on_separator(self, node):
    #     return node

    # def on_wtr(self, node):
    #     return node

    # def on_sep_word_dot(self, node):
    #     return node

    # def on_sep_word_period(self, node):
    #     return node

    # def on_sep_word_colon(self, node):
    #     return node

    # def on_sep_word_comma(self, node):
    #     return node

    # def on_sep_word_equal(self, node):
    #     return node

    # def on_z(self, node):
    #     return node

    # def on_sep_field(self, node):
    #     return node

    # def on_sep_line(self, node):
    #     return node

    # def on_brackets(self, node):
    #     return node

    # def on_abr(self, node):
    #     return node

    # def on_deletion(self, node):
    #     return node

    # def on_cpl(self, node):
    #     return node

    # def on_add(self, node):
    #     return node

    # def on_deletion_nested(self, node):
    #     return node

    # def on_lost(self, node):
    #     return node

    # def on_unknown(self, node):
    #     return node

    # def on_known(self, node):
    #     return node

    # def on_space(self, node):
    #     return node

    # def on_prettyspace(self, node):
    #     return node

    # def on_EOF(self, node):
    #     return node



compiling: Junction = Junction(
    'AST', ThreadLocalSingletonFactory(eceCompiler), 'ece')

get_compiler = compiling.factory  # for backwards compatibility, only


#######################################################################
#
# END OF DHPARSER-SECTIONS
#
#######################################################################

#######################################################################
#
# Post-Processing-Stages [add one or more postprocessing stages, here]
#
#######################################################################
from DHParser import ALLOWED_PRESET_VALUES

# class PostProcessing(Compiler):
#     ...

# # change the names of the source and destination stages. Source
# # ("ece") in this example must be the name of some earlier stage, though.
# postprocessing: Junction = Junction(
#     "ece", ThreadLocalSingletonFactory(PostProcessing), "refined")
#
# DON'T FORGET TO ADD ALL POSTPROCESSING-JUNCTIONS TO THE GLOBAL
# "junctions"-set IN SECTION "Processing-Pipeline" BELOW!

#######################################################################
#
# Processing-Pipeline
#
#######################################################################

# Add your own stages to the junctions and target-lists, below
# (See DHParser.compile for a description of junctions)

# ADD YOUR OWN POST-PROCESSING-JUNCTIONS HERE:
junctions = set([ASTTransformation, compiling])

# put your targets of interest, here. A target is the name of result (or stage)
# of any transformation, compilation or postprocessing step after parsing.
# Serializations of the stages listed here will be written to disk when
# calling process_file() or batch_process() and also appear in test-reports.
targets = end_points(junctions)
# alternative: targets = set([compiling.dst])

# provide a set of those stages for which you would like to see the output
# in the test-report files, here. (AST is always included)
test_targets = set(j.dst for j in junctions)
# alternative: test_targets = targets

# add one or more serializations for those targets that are node-trees
serializations = expand_table(dict([('*', [get_config_value('default_serialization')])]))


#######################################################################
#
# Main program
#
#######################################################################

def pipeline(source: str,
             target: Union[str, Set[str]] = "ece",
             start_parser: str = "root_parser__",
             *, cancel_query: Optional[CancelQuery] = None) -> PipelineResult:
    """Runs the source code through the processing pipeline. If
    the parameter target is not the empty string, only the stages required
    for the given target will be passed. See :py:func:`compile_src` for the
    explanation of the other parameters.
    """
    global targets
    if target:
        target_set = set([target]) if isinstance(target, str) else target
    else:
        target_set = targets
    return full_pipeline(
        source, preprocessing.factory, parsing.factory, junctions, target_set,
        start_parser, cancel_query = cancel_query)


def compile_src(source: str,
                target: str = "ece",
                start_parser: str = "root_parser__",
                *, cancel_query: Optional[CancelQuery] = None) -> Tuple[Any, List[Error]]:
    """Compiles the source to a single target and returns the result of the compilation
    as well as a (possibly empty) list or errors or warnings that have occurred in the
    process.

    :param source: Either a file name or a source text. Anything that is not a valid
        file name is assumed to be a source text. Add a byte-order mark ("\ufeff")
        at the beginning of short, i.e. one-line source texts, to avoid these being
        misinterpreted as filenames.
    :param target: the name of the target stage up to which the processing pipeline
        will be proceeded
    :param start_parser: the parser with which the parsing shall start. The default
        is the root-parser, but if only snippets of a full document shall be processed,
        it makes sense to pick another parser, here.

    :returns: a tuple (data, list of errors) of the data in the format of the
        target-stage selected by parameter "target" and of the potentially
        empty list of errors.
    """
    full_compilation_result = pipeline(source, target, start_parser)
    return full_compilation_result[target]


def compile_snippet(source_code: str,
                    target: str = "ece",
                    start_parser: str = "root_parser__",
                    *, cancel_query: Optional[CancelQuery] = None) -> Tuple[Any, List[Error]]:
    """Compiles a piece of source_code. In contrast to :py:func:`compile_src` the
    parameter source_code is always understood as a piece of source-code and never
    as a filename, not even if it is a one-liner that could also be a file-name.
    """
    if source_code[0:1] not in ('\ufeff', '\ufffe') and \
            source_code[0:3] not in ('\xef\xbb\xbf', '\x00\x00\ufeff', '\x00\x00\ufffe'):
        source_code = '\ufeff' + source_code  # add a byteorder-mark for disambiguation
    return compile_src(source_code, target, start_parser, cancel_query = cancel_query)


def process_file(source: str, out_dir: str = '', target_set: Set[str]=frozenset(),
                 *, cancel_query: CancelQuery = None) -> str:
    """Compiles the source and writes the serialized results back to disk,
    unless any fatal errors have occurred. Error and Warning messages are
    written to a file with the same name as `result_filename` with an
    appended "_ERRORS.txt" or "_WARNINGS.txt" in place of the name's
    extension. Returns the name of the error-messages file or an empty
    string, if no errors or warnings occurred.
    """
    global serializations, targets
    if not target_set:
        target_set = targets
    elif not target_set <= targets:
        raise AssertionError('Unknown compilation target(s): ' +
                             ', '.join(t for t in target_set - targets))
    # serializations = get_config_value('ece_serializations', serializations)
    return dsl.process_file(source, out_dir, preprocessing.factory, parsing.factory,
                            junctions, target_set, serializations, cancel_query)


def process_file_wrapper(args: Tuple[str, str, CancelQuery]) -> str:
    return process_file(args[0], args[1], cancel_query=args[2])


def batch_process(file_names: List[str], out_dir: str,
                  *, submit_func: Optional[Callable] = None,
                  log_func: Optional[Callable] = None,
                  cancel_func: Optional[Callable] = None) -> List[str]:
    """Compiles all files listed in file_names and writes the results and/or
    error messages to the directory `our_dir`. Returns a list of error
    messages files.
    """
    from eceParser import process_file_wrapper
    return dsl.batch_process(file_names, out_dir, process_file_wrapper,
        submit_func=submit_func, log_func=log_func, cancel_func=cancel_func)


def main(called_from_app=False) -> bool:
    global targets, test_targets, serializations, junctions
    # recompile grammar if needed
    scriptpath = os.path.abspath(os.path.realpath(__file__))
    if scriptpath.endswith('Parser.py'):
        grammar_path = scriptpath.replace('Parser.py', '.ebnf')
    else:
        grammar_path = os.path.splitext(scriptpath)[0] + '.ebnf'
    parser_update = False

    def notify():
        nonlocal parser_update
        parser_update = True
        print('recompiling ' + grammar_path)

    if os.path.exists(grammar_path) and os.path.isfile(grammar_path):
        if not recompile_grammar(grammar_path, scriptpath, force=False, notify=notify):
            error_file = os.path.basename(__file__)\
                .replace('Parser.py', '_ebnf_MESSAGES.txt')
            with open(error_file, 'r', encoding="utf-8") as f:
                print(f.read())
            sys.exit(1)
        elif parser_update:
            if '--dontrerun' in sys.argv:
                print(os.path.basename(__file__) + ' has changed. '
                      'Please run again in order to apply updated compiler')
                sys.exit(0)
            else:
                import platform, subprocess
                call = [sys.executable, __file__, '--dontrerun'] + sys.argv[1:]
                result = subprocess.run(call, capture_output=True)
                print(result.stdout.decode('utf-8'))
                sys.exit(result.returncode)
    else:
        print('Could not check whether grammar requires recompiling, '
              'because grammar was not found at: ' + grammar_path)

    from argparse import ArgumentParser
    a = "an" if "ece"[0:1] in "AEIOUaeiou" else "a"
    parser = ArgumentParser(description="Parses " + a + " ece file and shows its syntax-tree."
                            " If several filenames are provided or an output directory is "
                            "specified with --out, the results will be written to the disk!"
                            " To directly process content, use a pipe | e.g. "
                            ' echo "..." | eceParser.py.')
    parser.add_argument('files', nargs='*')
    parser.add_argument('-p', '--parse', nargs=1, default=[],
                        help='Processes the given snippet directly (instead of a file).')
    parser.add_argument('-d', '--debug', action='store_const', const='debug',
                        help='Write debug information to LOGS subdirectory')
    parser.add_argument('-o', '--out', nargs=1, default=['out'],
                        help='Output directory for batch processing')
    parser.add_argument('-v', '--verbose', action='store_const', const='verbose',
                        help='Verbose output')
    parser.add_argument('-f', '--force', action='store_const', const='force',
                        help='Write output file even if errors have occurred')
    parser.add_argument('--singlethread', action='store_const', const='singlethread',
                        help='Run batch jobs in a single thread (recommended only for debugging)')
    parser.add_argument('--dontrerun', action='store_const', const='dontrerun',
                        help='Do not automatically run again if the grammar has been recompiled.')
    parser.add_argument('-s', '--serialize', nargs=1, default=[],
                        help="Choose serialization format for tree structured data. Available: "
                             + ', '.join(ALLOWED_PRESET_VALUES['default_serialization']))
    parser.add_argument('-t', '--target', nargs='+', default=[],
                        help='Pick compilation target(s). Available targets: '
                             '%s; default: %s' % (', '.join(test_targets), ', '.join(targets)))

    args = parser.parse_args()
    file_names, out, log_dir = args.files, args.out[0], ''
    piped_data = '' if sys.stdin.isatty() else sys.stdin.read()
    if piped_data: file_names.insert(0, '\ufeff' + piped_data)
    if args.parse: file_names.insert(0, '\ufeff' + args.parse[0])

    if not file_names and not called_from_app:
        print("missing argument: files")
        sys.exit(1)
    if len(file_names) > 1:
        if piped_data:
            print("Cannot process piped data and snippet or files at the same time!")
            sys.exit(1)
        if args.parse:
            print('Cannot process snippet and files at the same time! '
                  '(Snippets that contain blanks need to be enclosed in quotes "..."')
            sys.exit(1)

    read_local_config(os.path.join(scriptdir, 'eceConfig.ini'))

    if args.serialize:
        if (args.serialize[0].lower() not in
                [sf.lower() for sf in ALLOWED_PRESET_VALUES['default_serialization']]):
            print('Unknown serialization format: ' + args.serialize[0] +
                  '! Available formats for tree-structures: '
                  + ', '.join(ALLOWED_PRESET_VALUES['default_serialization']))
            sys.exit(1)
        serializations['*'] = args.serialize
        access_presets()
        set_preset_value('ece_serializations', serializations, allow_new_key=True)
        finalize_presets()

    if args.debug is not None:
        log_dir = 'LOGS'
        access_presets()
        set_preset_value('history_tracking', True)
        set_preset_value('resume_notices', True)
        set_preset_value('log_syntax_trees', frozenset(['CST', 'AST']))  # don't use a set literal, here!
        start_logging(log_dir)
        finalize_presets()

    if args.singlethread:
        set_config_value('batch_processing_parallelization', False)

    if args.target:
        chosen = set(args.target)
        unknown = chosen - test_targets
        if unknown:
            print('Unknown targets: ' + ', '.join(unknown) + ' chosen!' +
                  '\nAvailable targets: ' + ', '.join(test_targets))
            sys.exit(1)
        targets = chosen

    def echo(message: str):
        if args.verbose:
            print(message)

    if called_from_app and not file_names:  return False

    batch_processing = True
    if len(file_names) <= 1:
        if os.path.isdir(file_names[0]):
            dir_name = file_names[0]
            echo('Processing all files in directory: ' + dir_name)
            file_names = [os.path.join(dir_name, fn) for fn in os.listdir(dir_name)
                          if fn[0:1] != '.' and os.path.isfile(os.path.join(dir_name, fn))]
        elif not ('-o' in sys.argv or '--out' in sys.argv):
            batch_processing = False

    if batch_processing:
        if not os.path.exists(out):
            os.mkdir(out)
        elif not os.path.isdir(out):
            print('Output directory "%s" exists and is not a directory!' % out)
            sys.exit(1)
        error_files = batch_process(file_names, out, log_func=print if args.verbose else None)
        if error_files:
            category = "ERRORS" if any(f.endswith('_ERRORS.txt') for f in error_files) \
                else "warnings"
            print("There have been %s! Please check files:" % category)
            print('\n'.join(error_files))
            if category == "ERRORS":
                sys.exit(1)
    else:
        if len(targets) == 1:
            result, errors = compile_src(file_names[0], target=next(iter(targets)))
        else:
            result, errors = compile_src(file_names[0])  # keep default_target

        if not errors or (not has_errors(errors, ERROR)) \
                or (not has_errors(errors, FATAL) and args.force):
            print(result.serialize(serializations['*'][0])
                  if isinstance(result, Node) else result)
            if errors:  print('\n---')

        for err_str in canonical_error_strings(errors):
            print(err_str)
        if has_errors(errors, ERROR):  sys.exit(1)

    return True


if __name__ == "__main__":
    main()
