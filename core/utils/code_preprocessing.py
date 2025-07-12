import re


def remove_imports(content):
    # Removes 'import module' and 'from module import name'
    content = re.sub(r"^\s*import\s+.*", "", content, flags=re.MULTILINE)
    content = re.sub(r"^\s*from\s+.*\s+import\s+.*", "", content, flags=re.MULTILINE)
    return content


def remove_packages(content):
    return content  # Python doesnt use packages


def remove_comments(content):
    """
    Removes all comments from the given PYTHON source code file.

        Parameters:
            content (string): The contents of the source code file.

        Returns:
            file_contents (string): The contents of the source code file with all comments removed.
    """
    # Pattern to match string literals and comments
    pattern = r"""
        ('''[\s\S]*?'''      # triple-quoted single-line or multi-line strings (single quotes)
        |\"\"\"[\s\S]*?\"\"\"     # triple-quoted single-line or multi-line strings (double quotes)
        |'[^'\\]*(?:\\.[^'\\]*)*'   # single-quoted string literals
        |"[^"\\]*(?:\\.[^"\\]*)*"   # double-quoted string literals
        )
        |(\#.*?$)           # single-line comments (captures the '#' )
    """
    regex = re.compile(pattern, re.MULTILINE | re.VERBOSE)

    def _replacer(match):
        # If the 2nd group is not None we have captured
        # a non-quoted (real) comment string.
        if match.group(2) is not None:
            return ""  # so we will return empty to remove the comment
        else:  # otherwise, we will return the 1st group
            return match.group(1)  # captured quoted-string

    return regex.sub(_replacer, content)


def remove_blank_lines(content):
    """
    Removes all blank lines from the given source code file.

        Parameters:
            content (string): The contents of the source code file.

        Returns:
            result (string): The contents of the source code file with all blank lines removed.
    """
    result = "\n".join([line.rstrip() for line in content.splitlines() if line.strip()])
    return result


def replace_strings_and_chars(content):
    placeholder = "<$STRING>"
    string_pattern = r"([\"']{3})([\s\S]*?)\1|([\"'])(?:(?=(\\?))\4.)*?\3"
    return re.sub(string_pattern, placeholder, content, flags=re.DOTALL)


def replace_numbers(content):
    """
    Replaces all numbers with a placeholder.

        Parameters:
            content (string): The contents of the source code file.

        Returns:
            result (string): The contents of the source code file with all numbers replaced with a placeholder.
    """
    placeholder = "<$NUMBER>"

    result = re.sub(
        r"(?<!\w)[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?(?!\w)", placeholder, content
    )
    return result


def replace_booleans(content):
    """
    Replaces all booleans with a placeholder.

        Parameters:
            content (string): The contents of the source code file.

        Returns:
            result (string): The contents of the source code file with all booleans replaced with a placeholder.
    """
    placeholder = "<$BOOLEAN>"

    result = re.sub(r"\b(true|false)\b", placeholder, content, flags=re.IGNORECASE)
    return result


def tokenize_code(content):
    """
    Tokenizes the given source code file.

        Parameters:
            content (string): The contents of the source code file.

        Returns:
            tokens (list): The tokens of the source code file.
    """
    tokens = re.findall(r"[A-Za-z0-9_$]+", content)
    return tokens


def word_list_to_string(word_list):
    return " ".join(str(word) for word in word_list)


# JAVA PREPROCESSING
'''
def remove_imports(content):

    Removes all import statements from the given source code file.

        Parameters:
            content (string): The contents of the source code file.

        Returns:
            result (string): The contents of the source code file with all import statements removed.

    result = re.sub(r"import .*?;", "", content)
    return result

def remove_packages(content):
    """
    Removes all package statements from the given source code file.

        Parameters:
            content (string): The contents of the source code file.

        Returns:
            result (string): The contents of the source code file with all package statements removed.
    """
    result = re.sub(r"package .*?;", "", content)
    return result


def remove_comments(content):
    """
    Removes all comments from the given JAVA source code file.

        Parameters:
            content (string): The contents of the source code file.

        Returns:
            file_contents (string): The contents of the source code file with all comments removed.
    """
    # The 1st group captures quoted strings (double or single)
    # The 2nd group captures comments (//single-line or /* multi-line */)
    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
    regex = re.compile(pattern, re.MULTILINE | re.DOTALL)

    def _replacer(match):
        # If the 2nd group is not None we have captured
        # a non-quoted (real) comment string.
        if match.group(2) is not None:
            return ""  # so we will return empty to remove the comment
        else:  # otherwise, we will return the 1st group
            return match.group(1)  # captured quoted-string

    return regex.sub(_replacer, content)


def remove_blank_lines(content):
    """
    Removes all blank lines from the given source code file.

        Parameters:
            content (string): The contents of the source code file.

        Returns:
            result (string): The contents of the source code file with all blank lines removed.
    """
    result = "\n".join([line.rstrip() for line in content.splitlines() if line.strip()])
    return result


def replace_strings_and_chars(content):
    """
    Replaces all strings and characters with a placeholder.

        Parameters:
            content (string): The contents of the source code file.

        Returns:
            result (string): The contents of the source code file with all strings and characters replaced with a placeholder.
    """
    placeholder = "<$STRING>"

    result = re.sub(r"([\"\']){3}.*?\1{3}|([\"\']).*?\2", placeholder, content)
    return result


def replace_numbers(content):
    """
    Replaces all numbers with a placeholder.

        Parameters:
            content (string): The contents of the source code file.

        Returns:
            result (string): The contents of the source code file with all numbers replaced with a placeholder.
    """
    placeholder = "<$NUMBER>"

    result = re.sub(
        r"(?<!\w)[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?(?!\w)", placeholder, content
    )
    return result


def replace_booleans(content):
    """
    Replaces all booleans with a placeholder.

        Parameters:
            content (string): The contents of the source code file.

        Returns:
            result (string): The contents of the source code file with all booleans replaced with a placeholder.
    """
    placeholder = "<$BOOLEAN>"

    result = re.sub(r"\b(true|false)\b", placeholder, content, flags=re.IGNORECASE)
    return result


def tokenize_code(content):
    """
    Tokenizes the given source code file.

        Parameters:
            content (string): The contents of the source code file.

        Returns:
            tokens (list): The tokens of the source code file.
    """
    tokens = re.findall(r"[A-Za-z0-9_$]+", content)
    return tokens


def word_list_to_string(word_list):
    """Converts a list of words into a single string.

    Parameters:
        word_list (list): A list of words.

    Returns:
        (string): A string of words separated by spaces.
    """
    temp_list = []

    for word in word_list:
        if word is not str:
            word = str(word)
        temp_list.append(word)

    return " ".join(temp_list)

'''