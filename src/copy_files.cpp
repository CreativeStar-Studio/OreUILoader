#include <windows.h>
#include <iostream>
#include <filesystem>

// 定义导出函数
extern "C" __declspec(dllexport) void __stdcall copy_files(const char* temp_dir, const char* gamepath) {
    namespace fs = std::filesystem;

    fs::path temp(temp_dir);
    fs::path target(gamepath);

    // 遍历源目录下的所有文件
    for (const auto& entry : fs::recursive_directory_iterator(temp)) {
        if (fs::is_regular_file(entry)) {
            fs::path target_path = target / entry.path().filename();
            // 如果目标文件存在，先删除
            if (fs::exists(target_path)) {
                try {
                    fs::remove(target_path);
                }
                catch (const fs::filesystem_error& e) {
                    std::cerr << "删除目标文件错误: " << e.what()  << std::endl;
                    continue;
                }
            }
            // 执行复制操作
            try {
                fs::copy_file(entry.path(),  target_path, fs::copy_options::overwrite_existing);
            }
            catch (const fs::filesystem_error& e) {
                std::cerr << "复制文件错误: " << e.what()  << std::endl;
            }
        }
    }
}