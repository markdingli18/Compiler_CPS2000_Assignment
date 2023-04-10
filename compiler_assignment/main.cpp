#include <iostream>
#include <string>
#include <vector>
#include <cctype>
#include <unordered_map>
#include <stdexcept>
#include <array>

enum TokenType {
    IDENTIFIER,
    INTEGER_LITERAL,
    FLOAT_LITERAL,
    COLOUR_LITERAL,
    KEYWORD,
    OPERATOR,
    DELIMITER,
    BOOLEAN_LITERAL
};

struct Token {
    TokenType type;
    std::string value;
};

enum State {
    START,
    ID,
    NUMBER,
    COLOUR,
    BOOLEAN,
    ASSIGN
};

class Lexer {
public:
    Lexer(const std::string &input) : input(input), current(0), state(START) {}

    std::vector<Token> tokenize() {
        std::vector<Token> tokens;

        while (current < input.size()) {
            char c = input[current];
            int charClass = classifyChar(c);
            State nextState = transitionTable[state][charClass];

            switch (nextState) {
                case START:
                    if (isspace(c)) {
                        current++;
                    } else {
                        state = nextState;
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
                case BOOLEAN:
                    boolean(tokens);
                    break;
                case ASSIGN:  // new case for the ASSIGN state
                    tokens.push_back({OPERATOR, "="});
                    current++;
                    state = START;
                    break;
                default:
                    throw std::runtime_error("Unexpected character encountered: " + std::string(1, c));
            }
        }

        return tokens;
    }

    std::string tokenTypeToString(TokenType type) {
        switch(type) {
            case IDENTIFIER:
                return "IDENTIFIER";
            case INTEGER_LITERAL:
                return "INTEGER_LITERAL";
            case FLOAT_LITERAL:
                return "FLOAT_LITERAL";
            case COLOUR_LITERAL:
                return "COLOUR_LITERAL";
            case KEYWORD:
                return "KEYWORD";
            case OPERATOR:
                return "OPERATOR";
            case DELIMITER:
                return "DELIMITER";
            case BOOLEAN_LITERAL:
                return "BOOLEAN_LITERAL";
            default:
                return "UNKNOWN";
        }
    }

private:
    std::string input;
    std::size_t current;
    State state;

    enum CharClass {
        WHITESPACE,
        ALPHA,
        DIGIT,
        HASH,
        OPER,
        DELIM,
        INVALID
    };

    static const std::array<std::array<State, 7>, 6> transitionTable;

    CharClass classifyChar(char c) const {
        if (isspace(c)) return WHITESPACE;
        if (isalpha(c) || c == '_') return ALPHA;
        if (isdigit(c)) return DIGIT;
        if (c == '#') return HASH;
        if (operators.find(c) != std::string::npos) return OPER;
        if (delimiters.find(c) != std::string::npos) return DELIM;
        return INVALID;
    }

    void identifier(std::vector<Token> &tokens) {
        std::size_t start = current;

        while (current < input.size() && (isalnum(input[current]) || input[current] == '_')) {
            current++;
        }

        std::string value = input.substr(start, current - start);
        TokenType type;

        if (keywords.find(value) != keywords.end()) {
            type = KEYWORD;
        } else if (boolean_literals.find(value) != boolean_literals.end()) {
            type = BOOLEAN_LITERAL;
        } else {
            type = IDENTIFIER;
        }

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
            throw std::runtime_error("Invalid color literal (must have 6 hex digits): " + input.substr(current, input.size() - current));
        }

        std::string value = "#";

        for (int i = 0; i < 6; i++) {
            char c = input[current++];
            if (isdigit(c) || (c >= 'A' && c <= 'F') || (c >= 'a' && c <= 'f')) {
                value += c;
            } else {
                throw std::runtime_error("Invalid color literal (non-hex digit encountered): " + std::string(1, c));
            }
        }

        tokens.push_back({COLOUR_LITERAL, value});
        state = START;
    }

    void boolean(std::vector<Token> &tokens) {
        std::size_t start = current;

        while (current < input.size() && isalnum(input[current])) {
            current++;
        }

        std::string value = input.substr(start, current - start);

        if (boolean_literals.find(value) != boolean_literals.end()) {
            tokens.push_back({BOOLEAN_LITERAL, value});
        } else {
            throw std::runtime_error("Invalid boolean literal: " + value);
        }

        state = START;
    }

    std::unordered_map<std::string, int> keywords = {
            {"float", 1},
            {"int", 1},
            {"bool", 1},
            {"colour", 1},
            {"let", 1},
            {"fun", 1},
            {"if", 1},
            {"else", 1},
            {"for", 1},
            {"while", 1},
            {"return", 1},
            {"__width", 1},
            {"__height", 1},
            {"__read", 1},
            {"__randi", 1},
            {"__print", 1},
            {"__delay", 1},
            {"__pixel", 1},
            {"__pixelr", 1}
    };

    std::unordered_map<std::string, int> boolean_literals = {
            {"true", 1},
            {"false", 1}
    };

    const std::string operators = "*+/and- =<>=!";
    const std::string delimiters = "{},;()";
};

const std::array<std::array<State, 7>, 6> Lexer::transitionTable = {{
                                                                            //             WHITESPACE ALPHA   DIGIT    HASH     OPER     DELIM    INVALID
                                                                            /* START    */ { START,     ID,     NUMBER,  COLOUR,  ASSIGN,  START,   START },
                                                                            /* ID       */ { START,     ID,     ID,      START,   ASSIGN,  START,   START },
                                                                            /* NUMBER   */ { START,     ID,     NUMBER,  START,   ASSIGN,  START,   START },
                                                                            /* COLOUR   */ { START,     START,  START,   START,   ASSIGN,  START,   START },
                                                                            /* BOOLEAN  */ { START,     BOOLEAN,BOOLEAN, START,   ASSIGN,  START,   START },
                                                                            /* ASSIGN   */ { START,     START,  START,   START,   ASSIGN,  START,   START }
                                                                    }};


int main() {
    std::string input = "let x=12";
    std::cout << "\nInput: " << input << std::endl;
    Lexer lexer(input);

    try {
        std::vector<Token> tokens = lexer.tokenize();

        std::cout << "Number of tokens: " << tokens.size() << std::endl;
        std::cout << "\n" << std::string(120, '-') << std::endl;

        for (const auto &token : tokens) {
            std::cout << "Token type: " << lexer.tokenTypeToString(token.type) << " Value: " << token.value << std::endl;
        }
    } catch (std::runtime_error &e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }

    return 0;
}