package modules;

import com.google.inject.AbstractModule;
import com.google.inject.name.Names;

import java.io.IOException;
import java.util.Properties;

public class PropertiesModule extends AbstractModule {
    @Override
    public void configure() {
        try {
            Properties props = new Properties();
            props.load(getClass().getClassLoader().getResourceAsStream("logging.properties"));
            Names.bindProperties(binder(), props);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}
