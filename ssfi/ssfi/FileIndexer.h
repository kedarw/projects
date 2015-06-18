#include<iostream>
#include<string>
#include<fstream>
#include<sstream>

#include<vector>
#include<queue>
#include<map>

#include<thread>
#include<mutex>
#include<condition_variable>
#include<Windows.h>
#include "ctype.h"

// Class to hold all data structures needed for file indexer and
// functions which will be operating on these data structures
class FileIndexer{
private:
	std::mutex								mtx;
	std::condition_variable					cv;

	std::vector<std::map<std::string, int>> vector_of_maps;
	std::queue<std::wstring>				files_to_be_processed;
	bool									all_work_done;
	
	int										num_of_threads;
	std::thread								*worker_threads;

	//Declare functions
	void ParseFileForWords(std::wstring file_name, std::map<std::string, int>& words_count);
	void DeQueueFile(int id);
	void PrintResults();
	void SearchDirectory(const std::wstring &dir_path);

public:

	FileIndexer(int num_threads, const std::wstring &dir_path)
	{
		std::wcout << "Directory to be searched ........\t" << dir_path << std::endl << std::endl;
		std::cout << "Number of threads................\t" << num_threads << std::endl << std::endl;

		num_of_threads = num_threads;
		all_work_done = false;

		// Create worker threads
		worker_threads = new std::thread[num_of_threads];

		for (int i = 0; i < num_of_threads; i++)
		{
			vector_of_maps.push_back(std::map<std::string, int>());
			// Initialize worker threads to parse data
			worker_threads[i] = std::thread(&FileIndexer::DeQueueFile, this, i);
		}

		SearchDirectory(dir_path);
	}

	~FileIndexer()
	{
		{
			std::unique_lock<std::mutex> lck(mtx); //acquire lock to make operation on all_work_done atomic
			all_work_done = true;
		}// release lock

		//Notify all threads
		cv.notify_all();

		std::cout << "\nWaiting for all processing to be over, this may take time depending on input..." << std::endl << std::endl;

		for (int i = 0; i < num_of_threads; i++)
		{

			worker_threads[i].join();
		}

		//Print results before you exit
		PrintResults();

		delete[] worker_threads;
	}
};