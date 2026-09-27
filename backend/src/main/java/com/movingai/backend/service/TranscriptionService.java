package com.movingai.backend.service;

import org.springframework.core.io.FileSystemResource;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestClient;

import java.nio.file.Files;
import java.nio.file.Path;

@Service
public class TranscriptionService {

    private final RestClient openAiRestClient;

    public TranscriptionService(RestClient openAiRestClient) {
        this.openAiRestClient = openAiRestClient;
    }

    public String transcribe(Path audioPath) {

        if (audioPath == null || !Files.exists(audioPath)) {
            throw new IllegalArgumentException(
                    "Audio file does not exist: " + audioPath
            );
        }

        MultiValueMap<String, Object> parts =
                new LinkedMultiValueMap<>();

        parts.add(
                "file",
                new FileSystemResource(audioPath)
        );

        parts.add(
                "model",
                "gpt-4o-transcribe"
        );

        TranscriptionResponse response =
                openAiRestClient
                        .post()
                        .uri("/audio/transcriptions")
                        .contentType(MediaType.MULTIPART_FORM_DATA)
                        .body(parts)
                        .retrieve()
                        .body(TranscriptionResponse.class);

        if (response == null ||
                response.text() == null ||
                response.text().isBlank()) {

            throw new RuntimeException(
                    "OpenAI returned an empty transcription."
            );
        }

        return response.text();
    }

    private record TranscriptionResponse(
            String text
    ) {
    }
}