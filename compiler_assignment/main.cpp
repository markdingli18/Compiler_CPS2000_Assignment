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

enum State {
    START,
    ID,
    NUMBER,
    COLOUR
};

class Lexer {
public:
    Lexer(const std::string &input) : input(input), current(0), state(START) {}

    std::vector<Token> tokenize() {
        std::vector<Token> tokens;

        while (current < input.size()) {
            char c = input[current];
            switch (state) {
                case START:
                    if (isspace(c)) {
                        current++;
                    } else if (isalpha(c) || c == '_') {
                        state = ID;
                    } else if (isdigit(c)) {
                        state = NUMBER;
                    } else if (c == '#') {
                        state = COLOUR;
                        current++;
                    } else if (operators.find(c) != std::string::npos) {
                        tokens.push_back({OPERATOR, std::string(1, c)});
                        current++;
                    } else if (delimiters.find(c) != std::string::npos) {
                        tokens.push_back({DELIMITER, std::string(1, c)});
                        current++;
                    } else {
                        throw std::runtime_error("Unexpected character encountered: " + std::string(1, c));
                    }
                    break;
                case ID:
                    identifier(tokens);
                    break;
                case NUMBER:
                    number(tokens);
                    break;
                case COLOUR:
                    colour(tokens);
                    break;
            }
        }

        return tokens;
    }

private:
    std::string input;
    std::size_t current;
    State state;

    const std::string operators = "*+/and+-or<>=!:";
    const std::string delimiters = "{},;()";

    void identifier(std::vector<Token> &tokens) {
        std::size_t start = current;

        while (current < input.size() && (isalnum(input[current]) || input[current] == '_')) {
            current++;
        }

        std::string value = input.substr(start, current - start);
        TokenType type = keywords.find(value) != keywords.end() ? KEYWORD : IDENTIFIER;

        tokens.push_back({type, value});
        state = START;
    }

    void number(std::vector<Token> &tokens) {
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

        TokenType type = is_float ? FLOAT_LITERAL : INTEGER_LITERAL;
        tokens.push_back({type, input.substr(start, current - start)});
        state = START;
    }

    void colour(std::vector<Token> &tokens) {
        if (current + 6 >= input.size()) {
            throw std::runtime_error("Invalid colour format (too short): " + input.substr(current));
        }

        std::string value = input.substr(current, 7);
        value.pop_back(); // Remove the trailing semicolon
        current += 7;

        for (size_t i = 1; i < value.size(); ++i) {
            if (!isxdigit(value[i])) {
                throw std::runtime_error("Invalid colour format (non-hex digit): " + value);
            }
        }

        tokens.push_back({COLOUR_LITERAL, value});
        state = START;
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