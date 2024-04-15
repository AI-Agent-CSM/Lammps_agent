"""
TEI (Text Encoding Initiative) XML processing module
"""

import datetime
import hashlib


from bs4 import BeautifulSoup
from dateutil import parser
from nltk.tokenize import sent_tokenize

from article import Article
from table import Table
from text import Text


class TEI:
    """
    Methods to transform TEI (Text Encoding Initiative) XML into article objects.
    """

    @staticmethod
    def parse(stream, source):
        """
        Parses a TEI XML datastream and returns a processed article.

        Args:
            stream: handle to input data stream
            source: text string describing stream source, can be None

        Returns:
            Article
        """

        soup = BeautifulSoup(stream, "lxml")

        title = soup.title.text

        # Extract article metadata
        (
            published,
            publication,
            authors,
            affiliations,
            affiliation,
            reference,
        ) = TEI.metadata(soup)

        # Validate parsed data
        if not title and not reference:
            print("Failed to parse content - no unique identifier found")
            return None

        # Parse text sections
        sections = TEI.text(soup, title)

        # Derive uid
        uid = hashlib.sha1(
            title.encode("utf-8") if title else reference.encode("utf-8")
        ).hexdigest()

        # Default title to source if empty
        title = title if title else source

        # Article metadata - id, source, published, publication, authors, affiliations, affiliation, title,
        #                    tags, reference, entry date
        metadata = (
            uid,
            source,
            published,
            publication,
            authors,
            affiliations,
            affiliation,
            title,
            "PDF",
            reference,
            parser.parse(datetime.datetime.now().strftime("%Y-%m-%d")),
        )

        return Article(metadata, sections)

    @staticmethod
    def date(published):
        """
        Attempts to parse a publication date, if available. Otherwise, None is returned.

        Args:
            published: published object

        Returns:
            publication date if available/found, None otherwise
        """

        # Parse publication date
        # pylint: disable=W0702
        try:
            published = (
                parser.parse(published["when"])
                if published and "when" in published.attrs
                else None
            )
        except:
            published = None

        return published

    @staticmethod
    def authors(source):
        """
        Parses authors and associated affiliations from the article.

        Args:
            elements: authors elements

        Returns:
            (semicolon separated list of authors, semicolon separated list of affiliations, primary affiliation)
        """

        authors = []
        affiliations = []

        for name in source.find_all("persname"):
            surname = name.find("surname")
            forename = name.find("forename")

            if surname and forename:
                authors.append(f"{surname.text}, {forename.text}")

        for affiliation in source.find_all("affiliation"):
            names = [name.text for name in affiliation.find_all("orgname")]
            affiliations.append((", ".join(names)))

        return (
            "; ".join(authors),
            "; ".join(dict.fromkeys(affiliations)),
            affiliations[-1] if affiliations else None,
        )

    @staticmethod
    def metadata(soup):
        """
        Extracts article metadata.

        Args:
            soup: bs4 handle

        Returns:
            (published, publication, authors, reference)
        """

        # Build reference link
        source = soup.find("sourcedesc")
        if source:
            published = source.find("monogr").find("date")
            publication = source.find("monogr").find("title")

            # Parse publication information
            published = TEI.date(published)
            publication = publication.text if publication else None
            authors, affiliations, affiliation = TEI.authors(source)

            struct = soup.find("biblstruct")
            reference = (
                "https://doi.org/" + struct.find("idno").text
                if struct and struct.find("idno")
                else None
            )
        else:
            published, publication, authors, affiliations, affiliation, reference = (
                None,
                None,
                None,
                None,
                None,
                None,
            )

        return (published, publication, authors, affiliations, affiliation, reference)

    @staticmethod
    def abstract(soup, title):
        """
        Builds a list of title and abstract sections.

        Args:
            soup: bs4 handle
            title: article title

        Returns:
            list of sections
        """

        sections = [("TITLE", title)]

        abstract = soup.find("abstract").text
        if abstract:
            # Transform and clean text
            abstract = Text.transform(abstract)
            abstract = abstract.replace("\n", " ")

            sections.extend([("ABSTRACT", x) for x in sent_tokenize(abstract)])

        return sections
    

    @staticmethod
    def papers_references(soup):
        """
        Extracts references to other papers from the article.

        Args:
            soup: bs4 handle

        Returns:
            list of dictionaries containing paper reference information
        """
        references = []

        for biblStruct in soup.find_all("biblStruct"):
            # Initialize a dictionary to hold this reference's information
            reference = {}

            # Extract the title of the analytic work (if available)
            analytic_title = biblStruct.find("analytic").find("title") if biblStruct.find("analytic") else None
            if analytic_title and analytic_title.get("type") == "main":
                reference["title"] = analytic_title.text.strip()

            # Extract author names
            authors = []
            for author in biblStruct.find_all("author"):
                persName = author.find("persName")
                if persName:
                    forename = persName.find("forename").text.strip() if persName.find("forename") else ''
                    surname = persName.find("surname").text.strip() if persName.find("surname") else ''
                    authors.append(f"{forename} {surname}".strip())
            if authors:
                reference["authors"] = "; ".join(authors)

            # Extract the publication title
            monogr_title = biblStruct.find("monogr").find("title") if biblStruct.find("monogr") else None
            if monogr_title and monogr_title.get("level") == "m":
                reference["publication_title"] = monogr_title.text.strip()

            # Extract the publication date
            imprint_date = biblStruct.find("imprint").find("date") if biblStruct.find("imprint") else None
            if imprint_date and imprint_date.get("type") == "published":
                reference["publication_date"] = imprint_date["when"]

            # Append this reference to the list of references
            references.append(reference)

        return references

    @staticmethod
    def text(soup, title):
        """
        Builds a list of text sections.

        Args:
            soup: bs4 handle
            title: article title

        Returns:
            list of sections
        """

        # Initialize with title and abstract text
        sections = TEI.abstract(soup, title)

        for section in soup.find("text").find_all("div", recursive=False):
            # Section name and text
            children = list(section.children)

            # Attempt to parse section header
            if children and not children[0].name:
                name = str(children[0]).upper()
                children = children[1:]
            else:
                name = None

            text = " ".join(
                [str(e.text) if hasattr(e, "text") else str(e) for e in children]
            )
            text = text.replace("\n", " ")

            # Transform and clean text
            text = Text.transform(text)

            # Split text into sentences, transform text and add to sections
            sections.extend([(name, x) for x in sent_tokenize(text)])

        # Extract text from tables
        for i, figure in enumerate(soup.find("text").find_all("figure")):
            # Use XML Id (if available) as figure name to ensure figures are uniquely named
            name = figure.get("xml:id")
            name = name.upper() if name else f"FIGURE_{i}"

            # Search for table
            table = figure.find("table")
            if table:
                sections.extend([(name, x) for x in Table.extract(table)])

        return sections