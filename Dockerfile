FROM python

RUN mkdir /pdns-cli
COPY --chown=0:0 ./ /pdns-cli/
WORKDIR /pdns-cli
RUN pip install -r requirements.txt
USER nobody
ENTRYPOINT /pdns-cli/pdns
