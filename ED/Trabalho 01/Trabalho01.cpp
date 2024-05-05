/**************************************************
*
* Cauê Maldonado Lima
* Ryan Breda Santos
* Trabalho de Estruturas de Dados
* Professor: Diego Padilha Rubert 
*
*/

#include <iostream>
#include <fstream>
#include <queue>
#include <unordered_map>
#include <vector>
#include <bitset>

using namespace std;

// Estrutura de nó para a árvore de Huffman
struct HuffmanNode {
    char data;
    int freq;
    HuffmanNode *left, *right;
    
    HuffmanNode(char data, int freq) : data(data), freq(freq), left(nullptr), right(nullptr) {}
};

// Comparador para a fila de prioridade min-heap
struct Compare {
    bool operator()(HuffmanNode* l, HuffmanNode* r) {
        return l->freq > r->freq;
    }
};

// Função para calcular frequências dos caracteres
unordered_map<char, int> calculateFrequencies(const string& text) {
    unordered_map<char, int> freqMap;
    for (char c : text) {
        freqMap[c]++;
    }
    return freqMap;
}

// Função para criar a árvore de Huffman
HuffmanNode* buildHuffmanTree(const unordered_map<char, int>& freqMap) {
    priority_queue<HuffmanNode*, vector<HuffmanNode*>, Compare> minHeap;

    for (auto& pair : freqMap) {
        minHeap.push(new HuffmanNode(pair.first, pair.second));
    }

    while (minHeap.size() != 1) {
        HuffmanNode *left = minHeap.top(); minHeap.pop();
        HuffmanNode *right = minHeap.top(); minHeap.pop();

        HuffmanNode *top = new HuffmanNode('$', left->freq + right->freq);
        top->left = left;
        top->right = right;

        minHeap.push(top);
    }
    return minHeap.top();
}

// Função para mapear os códigos dos caracteres
void generateCodes(HuffmanNode* root, string code, unordered_map<char, string>& huffmanCodes) {
    if (!root)
        return;

    if (root->data != '$')
        huffmanCodes[root->data] = code;

    generateCodes(root->left, code + "0", huffmanCodes);
    generateCodes(root->right, code + "1", huffmanCodes);
}

// Função para compactar o arquivo
void compressFile(const string& inputFile, const string& outputFile) {
    ifstream inFile(inputFile, ios::binary);
    ofstream outFile(outputFile, ios::binary);

    string text((istreambuf_iterator<char>(inFile)), istreambuf_iterator<char>());

    unordered_map<char, int> freqMap = calculateFrequencies(text);
    HuffmanNode* root = buildHuffmanTree(freqMap);

    unordered_map<char, string> huffmanCodes;
    generateCodes(root, "", huffmanCodes);

    // Escreve o cabeçalho com as frequências no arquivo compactado
    for (auto& pair : freqMap) {
        outFile << pair.first << pair.second;
    }
    outFile << '\n';

    // Escreve o texto compactado usando os códigos de Huffman
    string compressedText;
    for (char c : text) {
        compressedText += huffmanCodes[c];
    }

    // Escreve o texto compactado como sequência de bits
    bitset<8> bits;
    int bitCount = 0;
    for (char bit : compressedText) {
        if (bit == '1') {
            bits.set(bitCount);
        }
        bitCount++;
        if (bitCount == 8) {
            outFile << static_cast<char>(bits.to_ulong());
            bitCount = 0;
            bits.reset();
        }
    }
    if (bitCount > 0) {
        outFile << static_cast<char>(bits.to_ulong());
    }

    inFile.close();
    outFile.close();
}

// Função para descompactar o arquivo
void decompressFile(const string& inputFile, const string& outputFile) {
    ifstream inFile(inputFile, ios::binary);
    ofstream outFile(outputFile);

    // Lê o cabeçalho para reconstruir a árvore de Huffman
    unordered_map<char, int> freqMap;
    char c;
    int freq;
    while (inFile >> noskipws >> c >> freq) {
        freqMap[c] = freq;
    }
    inFile.get(); // Ignora o caractere de nova linha

    HuffmanNode* root = buildHuffmanTree(freqMap);

    // Descompacta o texto
    HuffmanNode* curr = root;
    char byte;
    while (inFile.get(byte)) {
        for (int i = 7; i >= 0; --i) {
            if (byte & (1 << i)) {
                curr = curr->right;
            } else {
                curr = curr->left;
            }
            if (curr->left == nullptr && curr->right == nullptr) {
                outFile << curr->data;
                curr = root;
            }
        }
    }

    inFile.close();
    outFile.close();
}

int main(int argc, char* argv[]) {
    if (argc != 4) {
        cout << "Uso: " << argv[0] << " [c/d] arquivo_entrada arquivo_saida\n";
        return 1;
    }

    string operation = argv[1];
    string inputFileName = argv[2];
    string outputFileName = argv[3];

    if (operation == "c") {
        compressFile(inputFileName, outputFileName);
    } else if (operation == "d") {
        decompressFile(inputFileName, outputFileName);
    } else {
        cout << "Operação inválida. Use 'c' para compressão ou 'd' para descompressão.\n";
        return 1;
    }

    return 0;
}
