#include <iostream>
#include <string>
#include <vector>
#include <cctype>
#include <unordered_map>
#include <stdexcept>

enum TokenType {
    IDENTIFIER,
    INTEGER_LITERAL,
    FLOAT_LITERAL,
    COLOUR_LITERAL,
    KEYWORD,
    OPERATOR,
    DELIMITER
};

struct Token {
    TokenType type;
    std::string value;
};

class Lexer {
public:
    Lexer(const std::string &input) : input(input), current(0) {}

    std::vector<Token> tokenize() {
        std::vector<Token> tokens;

        while (current < input.size()) {
            skipWhitespace();

            if (current >= input.size()) {
                break;
            }

            if (isalpha(input[current]) || input[current] == '_') {
                tokens.push_back(identifier());
            } else if (isdigit(input[current])) {
                tokens.push_back(number());
            } else if (input[current] == '#') {
                tokens.push_back(colour());
            } else if (operators.find(input[current]) != std::string::npos) {
                tokens.push_back(op());
            } else if (delimiters.find(input[current]) != std::string::npos) {
                tokens.push_back(delimiter());
            } else {
                throw std::runtime_error("Unexpected character encountered: " + std::string(1, input[current]));
            }
        }

        return tokens;
    }

private:
    std::string input;
    std::size_t current;

    const std::string operators = "*+/and+-or<>=!:";
    const std::string delimiters = "{},;()";

    void skipWhitespace() {
        while (current < input.size() && isspace(input[current])) {
            current++;
        }
    }

    Token identifier() {
        std::size_t start = current;

        while (current < input.size() && (isalnum(input[current]) || input[current] == '_')) {
            current++;
        }

        std::string value = input.substr(start, current - start);
        TokenType type = keywords.find(value) != keywords.end() ? KEYWORD : IDENTIFIER;

        return {type, value};
    }

    Token number() {
        std::size_t start = current;
        bool is_float = false;

        while (current < input.size() && (isdigit(input[current]) || input[current] == '.')) {
            if (input[current] == '.') {
                if (is_float) {
                    throw std::runtime_error("Invalid number format (multiple decimal points): " + input.substr(start, current - start + 1));
                }
                is_float = true;
            }
            current++;
        }

        std::string value = input.substr(start, current - start);
        TokenType type = is_float ? FLOAT_LITERAL : INTEGER_LITERAL;

        return {type, value};
    }

    Token colour() {
        if (current + 6 >= input.size()) {
            throw std::runtime_error("Invalid colour format (too short): " + input.substr(current));
        }

        std::string value = input.substr(current, 7);
        current += 7;

        for (size_t i = 1; i < value.size(); ++i) {
            if (!isxdigit(value[i])) {
                throw std::runtime_error("Invalid colour format (non-hex digit): " + value);
            }
        }

        return {COLOUR_LITERAL, value};
    }

    Token op() {
        std::string value = std::string(1, input[current]);
        current++;

        return {OPERATOR, value};
    }

    Token delimiter() {
        std::string value = std::string(1, input[current]);
        current++;

        return {DELIMITER, value};
    }

    const std::unordered_map<std::string, TokenType> keywords = {
            {"let", KEYWORD}, {"true", KEYWORD}, {"false", KEYWORD},
            {"float", KEYWORD}, {"int", KEYWORD}, {"bool", KEYWORD}, {"colour", KEYWORD},
            {"__width", KEYWORD}, {"__height", KEYWORD}, {"__read", KEYWORD}, {"__randi", KEYWORD},
            {"__print", KEYWORD}, {"__delay", KEYWORD}, {"__pixelr", KEYWORD}, {"__pixel", KEYWORD},
            {"return", KEYWORD}, {"if", KEYWORD}, {"else", KEYWORD}, {"for", KEYWORD}, {"while", KEYWORD},
            {"fun", KEYWORD}, {"not", KEYWORD}
    };
};

int main() {
    std::string input = "let x: int = 42; let y: float = 3.14; let color: colour = #FFAABB; if (x < y) { __print x; }";
    Lexer lexer(input);
    std::vector<Token> tokens = lexer.tokenize();

    for (const Token &token : tokens) {
        std::cout << "Type: " << token.type << " | Value: " << token.value << std::endl;
    }

    return 0;
}