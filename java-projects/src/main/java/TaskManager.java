import logger.SugaredLogger;

import java.util.concurrent.CompletableFuture;

public class TaskManager {
    private final SugaredLogger logger;

    public TaskManager() {
        this.logger = SugaredLogger.getLogger(System.out);
    }

    public CompletableFuture<Void> execute() {
        final String[] sentence = "This is a tutorial on Dependency Injection!".split(" ");
        for (final String word : sentence) {
            logger.write(word);
        }
        return logger.flushAsync()
                .whenComplete((__, throwable) -> {
                    if (throwable != null) {
                        throwable.printStackTrace();
                    } else {
                        logger.close();
                    }
                });
    }
}
