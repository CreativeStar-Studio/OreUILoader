import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;

public class FileReplacer {

    // 复制文件逻辑
    public static int replaceFiles(File sourceDir, File targetDir) {
        int fileCount = 0;
        File[] sourceFiles = sourceDir.listFiles();
        if (sourceFiles!= null) {
            for (File sourceFile : sourceFiles) {
                if (sourceFile.isFile())  {
                    File targetFile = new File(targetDir, sourceFile.getName());
                    try {
                        Files.copy(sourceFile.toPath(),  targetFile.toPath(),  StandardCopyOption.REPLACE_EXISTING);
                        System.out.println("  已复制 " + sourceFile.getPath()  + " 至 " + targetFile.getPath());
                        fileCount++;
                    } catch (IOException e) {
                        System.err.println("  替换文件 " + sourceFile.getName()  + " 时出错: " + e.getMessage());
                    }
                } else if (sourceFile.isDirectory())  {
                    File newTargetDir = new File(targetDir, sourceFile.getName());
                    if (!newTargetDir.exists())  {
                        newTargetDir.mkdirs();
                    }
                    fileCount += replaceFiles(sourceFile, newTargetDir);
                }
            }
        }
        return fileCount;
    }

    // 删除文件逻辑
    public static int deleteFiles(File dir) {
        int deletedFileCount = 0;
        File[] files = dir.listFiles();
        if (files!= null) {
            for (File file : files) {
                if (file.isFile())  {
                    if (file.delete())  {
                        System.out.println("  已删除 " + file.getName()  + "，源文件位置 " + file.getParent());
                        deletedFileCount++;
                    } else {
                        System.err.println("  删除文件 " + file.getName()  + " 失败，源文件位置 " + file.getParent());
                    }
                } else if (file.isDirectory())  {
                    deletedFileCount += deleteFiles(file);
                    if (file.delete())  {
                        System.out.println("  已删除目录 " + file.getName()  + "，源文件位置 " + file.getParent());
                    } else {
                        System.err.println("  删除目录 " + file.getName()  + " 失败，源文件位置 " + file.getParent());
                    }
                }
            }
        }
        return deletedFileCount;
    }

    // 恢复文件逻辑
    public static int restoreFiles(File sourceDir, File targetDir) {
        int fileCount = 0;
        File[] sourceFiles = sourceDir.listFiles();
        if (sourceFiles!= null) {
            for (File sourceFile : sourceFiles) {
                if (sourceFile.isFile())  {
                    File targetFile = new File(targetDir, sourceFile.getName());
                    try {
                        Files.copy(sourceFile.toPath(),  targetFile.toPath(),  StandardCopyOption.REPLACE_EXISTING);
                        System.out.println("  已恢复 " + sourceFile.getPath()  + " 至 " + targetFile.getPath());
                        fileCount++;
                    } catch (IOException e) {
                        System.err.println("  恢复文件 " + sourceFile.getName()  + " 时出错: " + e.getMessage());
                    }
                } else if (sourceFile.isDirectory())  {
                    File newTargetDir = new File(targetDir, sourceFile.getName());
                    if (!newTargetDir.exists())  {
                        newTargetDir.mkdirs();
                    }
                    fileCount += restoreFiles(sourceFile, newTargetDir);
                }
            }
        }
        return fileCount;
    }

    public static void main(String[] args) {
        if (args.length  < 3) {
            System.out.println("  请提供三个参数：临时目录路径、目标游戏路径和操作类型（replace/delete/restore）");
            return;
        }

        String tempDir = args[0];
        String gamePath = args[1];
        String operation = args[2];

        File tempSourceDir;
        File targetDir = new File(gamePath + "/data/gui/dist/hbui");

        if ("restore".equals(operation)) {
            tempSourceDir = new File(tempDir);
        } else {
            tempSourceDir = new File(tempDir + "/ui/hbui");
        }

        if (!tempSourceDir.exists()  ||!targetDir.exists())  {
            System.out.println("  临时目录或目标游戏路径不存在");
            return;
        }

        if ("replace".equals(operation)) {
            int fileCount = replaceFiles(tempSourceDir, targetDir);
            System.out.println("  总计 已复制 " + tempSourceDir.getPath()  + " 至 " + targetDir.getPath()  + " 目录中，共计 " + fileCount + " 文件");
        } else if ("delete".equals(operation)) {
            int deletedFileCount = deleteFiles(tempSourceDir);
            System.out.println("  总计 已删除 " + deletedFileCount + " 个文件");
        } else if ("restore".equals(operation)) {
            int fileCount = restoreFiles(tempSourceDir, targetDir);
            System.out.println("  总计 已恢复 " + tempSourceDir.getPath()  + " 至 " + targetDir.getPath()  + " 目录中，共计 " + fileCount + " 文件");
        }
    }
}
