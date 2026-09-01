package com.heritage.kalvettu.web;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

/**
 * SPA deep-link fallback.
 *
 * Paths beginning with `assets` or `api`, or containing a dot (real static files
 * such as index.html / favicon.svg), are excluded by the negative-lookahead regex
 * and are handled by Spring's static-resource handler / REST controllers.
 *
 * Every other GET is a client-side route; we forward to the built index.html so
 * React Router can resolve it. Forwarding (not reading the file directly) reuses
 * the resource handler that already serves /assets correctly.
 */
@Controller
public class SpaFallback {

    @RequestMapping({
        "/",
        "/{p:^(?!assets|api|.*\\.).+}",
        "/{p:^(?!assets|api|.*\\.).+}/{q}",
        "/{p:^(?!assets|api|.*\\.).+}/{q}/{r}",
        "/{p:^(?!assets|api|.*\\.).+}/{q}/{r}/{s}"
    })
    public String index() {
        return "forward:/index.html";
    }
}
