package logger;

import exceptions.LoggingException;

import java.util.concurrent.CompletableFuture;

public interface Logger {

    boolean write(String data);

    CompletableFuture<Void> flushAsync();

    boolean close();
}
