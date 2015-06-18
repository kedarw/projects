#include"FileIndexer.h"

//Function to open, parse file and put words in map with their count
void FileIndexer::ParseFileForWords(std::wstring file_name, std::map<std::string, int>& words_count)
{
	std::ifstream file(file_name);
	std::string word;
	std::string line;
	char c;
	
	std::wcout << "Parsing file " << file_name << std::endl;

	while (!file.eof())
	{
		std::getline(file, line); //Get line and process character by character to minimize disk accesses
		for (unsigned int i = 0; i < line.length(); i++)
		{
			c = line[i];

			if (isalnum((unsigned char)c)) // check if character is alphanumeric 
			{
				word.push_back(c);
			}
			else
			{
				if (word.length() == 0) //if word is empty continue loop
				{
					continue;
				}
				else //check map and insert word
				{

					if (words_count.find(word) != words_count.end())
					{
						++words_count[word];
					}
					else
					{
						words_count.insert({ word, 1 });
					}
				}
				word.clear();
			}
		}
		line.clear();
	}

	file.close();
}

// Remove file from queue by taking care of concurrency and
// pass it for parsing
void FileIndexer::DeQueueFile(int id)
{
	std::wstring file;

	while (true)
	{
		{
			std::unique_lock<std::mutex> lck(mtx); //acquire lock
			
			while (!all_work_done && files_to_be_processed.empty())
			{
				cv.wait(lck); // wait if there is no data to be processed
			}

			if (all_work_done) // destructor will set this flag and join all threads
				return;

			file = files_to_be_processed.front();
			files_to_be_processed.pop();
		} //release lock

		ParseFileForWords(file, vector_of_maps[id]);
	}
}

// This function SearchDirectory is taken from http://stackoverflow.com/questions/9414017/search-files-with-unicode-names
// It recursively searches for txt files in given folder
// Once it finds file, it pushes it in queue and notify sleeping thread to work on it(function DeQueueFile)
void FileIndexer::SearchDirectory(const std::wstring        &refcstrRootDirectory)
{
	std::wstring    strFilePath;					// Filepath
	std::wstring    strPattern;						// Pattern
	std::wstring    strExtension;					// Extension
	HANDLE          hFile;							// Handle to file
	WIN32_FIND_DATA FileInformation;				// File information
	std::wstring    refcstrExtension = L"txt";		// File extension
	bool            bSearchSubdirectories = true;	// Flag indicating search in subdirectories

	strPattern = refcstrRootDirectory + L"\\*.*";

	hFile = ::FindFirstFile(strPattern.c_str(), &FileInformation);
	if (hFile != INVALID_HANDLE_VALUE)
	{
		do
		{
			if (FileInformation.cFileName[0] != '.')
			{
				strFilePath.erase();
				strFilePath = refcstrRootDirectory + L"\\" + FileInformation.cFileName;

				if (FileInformation.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)
				{
					if (bSearchSubdirectories)
					{
						// Search subdirectory
						SearchDirectory(strFilePath);
					}
				}
				else
				{
					// Check extension
					strExtension = FileInformation.cFileName;
					strExtension = strExtension.substr(strExtension.rfind(L".") + 1);

					if (strExtension == refcstrExtension)
					{
						// Push filename in queue
						{
							std::unique_lock<std::mutex> lck(mtx); //acquire lock before you access queue

							std::wcout << "Found file " << strFilePath << std::endl;
							files_to_be_processed.push(strFilePath);
						}

						cv.notify_one();
					}
				}
			}
		} while (::FindNextFile(hFile, &FileInformation) == TRUE);

		// Close handle
		::FindClose(hFile);

		DWORD dwError = ::GetLastError();
		if (dwError != ERROR_NO_MORE_FILES)
			return;
	}

	return;
}

//Class to store word and count occurances in an object
//Helper for comparison for priority queue
class word_record {
public:
	word_record(const std::string& word, int count) :
		word_(word), count_(count) {}
	std::string word_;
	int count_;
};

//Class to compare words in priority queue
//Helper for comparison for priority queue
class word_record_cmp {
public:
	bool operator() (const word_record& left, const word_record& right)
	{
		return left.count_ < right.count_;
	}
};

void FileIndexer::PrintResults()
{
	//Merge all maps
	std::map<std::string, int> all_words;
	if (vector_of_maps.size() != 0)
	{
		for (std::vector<std::map<std::string, int>>::iterator v_itr = vector_of_maps.begin(); v_itr != vector_of_maps.end(); ++v_itr)
		{
			std::map<std::string, int> temp_map = *v_itr;
			for (std::map<std::string, int>::iterator m_itr = temp_map.begin(); m_itr != temp_map.end(); ++m_itr)
			{
				if (all_words.find(m_itr->first) == all_words.end())
				{
					all_words.insert({ m_itr->first, m_itr->second });
				}
				else
				{
					all_words[m_itr->first] += m_itr->second;
				}
			}
		}
	}

	// Sort the words in map as per their count
	// Thought of using vector of pairs and doing partial 
	// sort but I think priority queue is better as it is
	// implemented as max_heap
	if (!all_words.empty())
	{
		std::cout << "\t\t\t Final result" << std::endl << std::endl;

		std::priority_queue<word_record, std::vector<word_record>, word_record_cmp> pq;
		for (std::map<std::string, int>::const_iterator word_itr = all_words.begin();
			word_itr != all_words.cend(); ++word_itr) {
			pq.emplace(word_record(word_itr->first, word_itr->second));
		}

		int i = 0;
		while (pq.size() > 0 && i < 10) {
			std::cout << "Rank: " << (i + 1) << " \t\tWord: " << pq.top().word_ << " \t\tCount: " << pq.top().count_ << std::endl;
			++i;
			pq.pop();
		}
	}
	else
	{
		std::cout << "No txt files were found in input folder" << std::endl << std::endl;
	}

	std::cout << std::endl;
}