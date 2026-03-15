FROM alpine:3.20

RUN apk add --no-cache dnsmasq bind-tools

COPY dnsmasq.conf /etc/dnsmasq.conf

EXPOSE 53/udp 53/tcp

CMD ["dnsmasq", "--no-daemon", "--log-queries"]
