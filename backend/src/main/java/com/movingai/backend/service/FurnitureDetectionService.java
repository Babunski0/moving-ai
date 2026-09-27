package com.movingai.backend.service;

import com.movingai.backend.dto.FurnitureDetectionResponse;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import tools.jackson.databind.json.JsonMapper;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@Service
public class FurnitureDetectionService {

    private final JsonMapper jsonMapper;

    private final String pythonPath;
    private final String scriptPath;

    public FurnitureDetectionService(
            JsonMapper jsonMapper,
            @Value("${vision.python-path}") String pythonPath,
            @Value("${vision.script-path}") String scriptPath
    ) {
        this.jsonMapper = jsonMapper;
        this.pythonPath = pythonPath;
        this.scriptPath = scriptPath;
    }

    public FurnitureDetectionResponse detect(
            Path framesDirectory
    ) {

        try {

            ProcessBuilder processBuilder =
                    new ProcessBuilder(
                            pythonPath,
                            scriptPath,
                            framesDirectory.toString()
                    );

            processBuilder.redirectError(
                    ProcessBuilder.Redirect.INHERIT
            );

            Process process = processBuilder.start();

            String output;

            try (
                    BufferedReader reader =
                            new BufferedReader(
                                    new InputStreamReader(
                                            process.getInputStream()
                                    )
                            )
            ) {

                output = reader
                        .lines()
                        .collect(
                                Collectors.joining(
                                        System.lineSeparator()
                                )
                        );
            }

            boolean finished =
                    process.waitFor(
                            10,
                            TimeUnit.MINUTES
                    );

            if (!finished) {

                process.destroyForcibly();

                throw new RuntimeException(
                        "Furniture detection timed out."
                );
            }

            if (process.exitValue() != 0) {
                throw new RuntimeException(
                        "Furniture detection failed."
                );
            }

            if (output == null || output.isBlank()) {
                throw new RuntimeException(
                        "Furniture detector returned no output."
                );
            }

            return jsonMapper.readValue(
                    output,
                    FurnitureDetectionResponse.class
            );

        } catch (Exception e) {

            throw new RuntimeException(
                    "Failed to run furniture detection.",
                    e
            );
        }
    }
}