#include <iostream>
#include <string>
#include <sstream>
#include <map>
#include <vector>
#include <algorithm>
#include <cctype>

using namespace std;

string normalize_word(string word, bool case_sensitive) {
    word.erase(remove_if(word.begin(), word.end(), ::ispunct), word.end());
    if (!case_sensitive) {
        transform(word.begin(), word.end(), word.begin(), ::tolower);
    }
    return word;
}

map<string, int> count_words(const string& text, bool case_sensitive) {
    map<string, int> word_count;
    istringstream iss(text);
    string word;
    
    while (iss >> word) {
        word = normalize_word(word, case_sensitive);
        if (!word.empty()) word_count[word]++;
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
    istringstream iss(text);
    string word;
    
    while (iss >> word) {
        word = normalize_word(word, case_sensitive);
        if (word == target) return true;
    }
    
    return false;
}

int main(int argc, char* argv[]) {
    setlocale(LC_ALL, "");
    string text, line;
    while (getline(cin, line)) text += line + "\n";

    text.erase(remove(text.begin(), text.end(), '\n'), text.end());
    
    string sort_mode = "frequency";
    bool ascending = false;
    string search_target = "";
    bool case_sensitive = false;
    
    if (argc > 1) {
        for (int i = 1; i < argc; ++i) {
            string arg = argv[i];
            if (arg == "--frequency") sort_mode = "frequency";
            else if (arg == "--alphabet") sort_mode = "alphabet";
            else if (arg == "--length") sort_mode = "length";
            else if (arg == "--ascending") ascending = true;
            else if (arg == "--case-sensitive") case_sensitive = true;
            else if (arg == "--search" && i + 1 < argc) {
                search_target = argv[i + 1];
                i++;
            }
        }
    }
    
    auto word_counts = count_words(text, case_sensitive);
    int total_words = 0;
    for (const auto& [word, count] : word_counts) {
        total_words += count;
    }
    
    auto sorted_words = sort_words(word_counts, sort_mode, ascending);
    
    cout << "total_words: " << total_words << "\n";
    cout << "unique_words: " << word_counts.size() << "\n";
    
    for (const auto& [word, count] : sorted_words) {
        cout << word << "\t" << count << "\n";
    }
    
    if (!search_target.empty()) {
        bool found = search_word(text, search_target, case_sensitive);
        cout << "search_found: " << (found ? "true" : "false") << "\n";
    }
    
    return 0;
}