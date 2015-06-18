#include<iostream>
#include"FileIndexer.h"

// main function is kept to minimum possible functionality
// just call file indexer class object with number of threads and directory path
int main(int argc, char *argv[])
{
	if (argc != 4)
	{
		std::cout << "\nUsage ssfi -t <number of worker threads> 'dir to search files'\n";
		return -1;
	}
	
	int				num_threads		= atoi(argv[2]);
	std::string		dir				= argv[3];

	std::wstring	dir_path(dir.begin(), dir.end());
	
	FileIndexer FI(num_threads, dir_path);

	return 0;
}