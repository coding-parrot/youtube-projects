package modules;

import com.google.inject.AbstractModule;
import com.google.inject.Provides;
import com.google.inject.name.Named;
import logger.FastLogger;
import logger.Logger;
import logger.SugaredLogger;

import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.OutputStream;


public class LoggingModule extends AbstractModule {

    @Override
    public void configure() {
        bind(Logger.class).to(FastLogger.class);
    }

    @Provides
    @Named("file-output-stream")
    public OutputStream getOutputStream(@Named("output-file.name") String fileLocation) throws FileNotFoundException {
        return new FileOutputStream(fileLocation);
    }

    @Provides
    @Named("console-output-stream")
    public OutputStream getConsoleOutputStream(@Named("output-file.name") String fileLocation) throws FileNotFoundException {
        return System.out;
    }
}
