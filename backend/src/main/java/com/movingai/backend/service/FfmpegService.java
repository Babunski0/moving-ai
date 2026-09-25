package com.movingai.backend.service;

import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.concurrent.TimeUnit;

@Service
public class FfmpegService {

    public void extractAudio(Path videoPath, Path audioOutputPath) {
        List<String> command = List.of(
                "ffmpeg",
                "-y",
                "-i", videoPath.toString(),
                "-vn",
                "-ac", "1",
                "-ar", "16000",
                "-c:a", "pcm_s16le",
                audioOutputPath.toString()
        );

        runCommand(command);
    }

    public void extractFrames(Path videoPath, Path framesDirectory) {
        Path outputPattern = framesDirectory.resolve("frame-%04d.jpg");

        List<String> command = List.of(
                "ffmpeg",
                "-y",
                "-i", videoPath.toString(),
                "-vf", "fps=1/2",
                "-q:v", "2",
                outputPattern.toString()
        );

        runCommand(command);
    }

    private void runCommand(List<String> command) {
        try {
            ProcessBuilder processBuilder = new ProcessBuilder(command);

            processBuilder.redirectErrorStream(true);
            processBuilder.redirectOutput(ProcessBuilder.Redirect.INHERIT);

            Process process = processBuilder.start();

            boolean finished = process.waitFor(10, TimeUnit.MINUTES);

            if (!finished) {
                process.destroyForcibly();
                throw new RuntimeException("FFmpeg processing timed out.");
            }

            if (process.exitValue() != 0) {
                throw new RuntimeException(
                        "FFmpeg failed with exit code: " + process.exitValue()
                );
            }

        } catch (IOException e) {
            throw new RuntimeException(
                    "Could not start FFmpeg. Make sure FFmpeg is installed and available in PATH.",
                    e
            );

        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("FFmpeg processing was interrupted.", e);
        }
    }
}