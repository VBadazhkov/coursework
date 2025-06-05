#include <iostream>
#include <string>
#include <sstream>
#include <map>
#include <vector>
#include <algorithm>
#include <cctype>
#include <locale>

using namespace std;

string normalize_word(string word, bool case_sensitive) {
    word.erase(remove_if(word.begin(), word.end(), [](char c) { 
        return ispunct(static_cast<unsigned char>(c)); 
    }), word.end());
    
    if (!case_sensitive && !word.empty()) {
        transform(word.begin(), word.end(), word.begin(), ::tolower);
    }
    return word;
}

map<string, int> count_words(const string& text, bool case_sensitive, int& total_words) {
    map<string, int> word_count;
    istringstream iss(text);
    string word;
    total_words = 0;
    
    while (iss >> word) {
        word = normalize_word(word, case_sensitive);
        if (!word.empty()) {
            word_count[word]++;
            total_words++;
        }
    }
    
    return word_count;
}

vector<pair<string, int>> sort_words(const map<string, int>& words, const string& mode, bool ascending) {
    vector<pair<string, int>> vec(words.begin(), words.end());
    
    if (mode == "frequency") {
        sort(vec.begin(), vec.end(), [ascending](auto& a, auto& b) {
            return ascending ? a.second < b.second : a.second > b.second;
        });
    } else if (mode == "alphabet") {
        sort(vec.begin(), vec.end(), [ascending](auto& a, auto& b) {
            return ascending ? a.first < b.first : a.first > b.first;
        });
    } else if (mode == "length") {
        sort(vec.begin(), vec.end(), [ascending](auto& a, auto& b) {
            return ascending ? a.first.length() < b.first.length() : a.first.length() > b.first.length();
        });
    }
    
    return vec;
}

bool search_word(const string& text, string& target, bool case_sensitive) {
    target = normalize_word(target, case_sensitive);
    if (target.empty()) return false;
    
    istringstream iss(text);
    string word;
    
    while (iss >> word) {
        word = normalize_word(word, case_sensitive);
        if (word == target) return true;
    }
    
    return false;
}

int main(int argc, char* argv[]) {
    
    string text, line;
    while (getline(cin, line)) {
        text += line + " ";
    }
    
    replace(text.begin(), text.end(), '\n', ' ');
    text.erase(unique(text.begin(), text.end(), [](char a, char b) {
        return isspace(a) && isspace(b);
    }), text.end());
    if (!text.empty() && text.back() == ' ') text.pop_back();

    string sort_mode = "frequency";
    bool ascending = false;
    string search_target = "";
    bool case_sensitive = false;
    
    for (int i = 1; i < argc; ++i) {
        string arg = argv[i];
        if (arg == "--frequency") sort_mode = "frequency";
        else if (arg == "--alphabet") sort_mode = "alphabet";
        else if (arg == "--length") sort_mode = "length";
        else if (arg == "--ascending") ascending = true;
        else if (arg == "--case-sensitive") case_sensitive = true;
        else if (arg == "--search") {
            if (i + 1 < argc) {
                search_target = argv[++i];
            } else {
                cerr << "Error: --search requires a target word\n";
                return 1;
            }
        }
    }
    
    int total_words = 0;
    auto word_counts = count_words(text, case_sensitive, total_words);
    auto sorted_words = sort_words(word_counts, sort_mode, ascending);
    
    cout << "total_words: " << total_words << endl;
    cout << "unique_words: " << word_counts.size() << endl;
    
    for (const auto& [word, count] : sorted_words) {
        cout << word << "\t" << count << endl;
    }
    
    if (!search_target.empty()) {
        bool found = search_word(text, search_target, case_sensitive);
        cout << "search_found: " << (found ? "true" : "false") << endl;
    }
    
    return 0;
}
