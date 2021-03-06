A distributed forum / social media platform

    git clone git://github.com/dcramer/django-idmapper.git

Every document (forum message) forms two overlaying networks of nodes
that has a copy of that document. The networks are connected graphs,
and one of them is a strict subnetwork of the other one. The smaller
one is the "subscribing" set. Nodes in the subscribing set gets copies
of all comments to the document. The protocol is push-based: When you
have a peer that is subscribed to a document you have, and you have a
comment to that document, you send that comment to the peer. The
protocol attempts to keep the network for a document a connected graph
by allways electing a "root node" among themselves, and keeping track
of their distances from that root node. This way, no closed,
disconnected circles can form (circles can still form, bur they'r
obvious). This means that a document is only present on the nodes
actually interested in that particular document. It is a bit like what
NNTP would be, where nodes subscribe to newsgroups, if every message
had its own newsgroup.

Node A only pushes comments to document x to B if A and B share
document x. Every node should probably have a max-peers-per-document
setting to keep the branching level reasonable. For two nodes to
initiate contact, they both need to know a third node, and share the
same document with that third node. For eaxmple a "root document"

Every "virtual forum" consist of a root document, and you have to have
its id, and the address of a peer that also has it, to initiate
contact / usage of that forum. Every document (forum message) linked
from teh root, or from documents linked from the root (and so on)
forms its own network, and the original peer with the root document
need not be part of every such network.

You install i2p and cliqueclique on your machine, then go to
localhost:whatever in your browser. You enter a peer address and forum
root document id You _can_ of course run a node publicly as a website
too

My current django code supports multiple nodes in one installation,
each node connected to a django user object It's a rather simple idea
really. Only drawback I can think of is overhead :S


# Algorithms

## Metadata sync


### Node1 (server)
    Data:
     local: Its own data
     serial: Version of its data
     serialcopy: copy of the other nodes' copy of its own serial
     time=1

    When local changes:
      serial += 1
      time = 1

    While serial != serialcopy:
      Send (local, serial) to other node
      Wait time
      time *= 2

    When receiving:
      if received.serial == serial:
        serialcopy = serial
     

### Node2 (client)
    Data
      peer: a copy of the other nodes' data
      peerserial: copy of the other nodes' serial

    When receiving:
      Copy received.local to peer
      Send received.serial back to other node



## Metadata deletion


### Node1 (server)
    Data:
     local: Its own data

    While local exists:
     Send delete request to other node

    When receiving:
     Delete local


### Node2 (client)
    Data
      peer: a copy of the other nodes' data

    When receiving:
     Delete peer
     Send ACK to peer


## Stuff built on top of this protocol

### Directory

A directory is a set of documents that can not (directly) be listed
but that can be searched by prefix and matches can be listed. It is
intended for large collections of documents.

#### Basic idea

A tree structure where each node represents one more character in the
subject of (a set of) content document(s). The leaves are the content
documents. Thus any path down the tree represents a prefix of the
subject.



# Document formats
## Content document

    {"__smime_MIMESigned__": true,
     "header": {},
     "parts": [{"__email_mime_multipart_MIMEMultipart__": true,
                "parts": [{"__email_message_Message__": true,
                           "body": "",
                           "header": {"part_type": "content",
                                      "Content-Type": "text/plain; charset=\"utf-8\""}}],
                "header": {}}]}


## Links

    {"__smime_MIMESigned__": true,
     "header": {},
     "parts": [{"__email_mime_multipart_MIMEMultipart__": true,
                "parts": [{"__email_message_Message__": true,
                           "body": "",
                           "header": {"part_type": "link",
                                      "link_direction": "reversed"|"natural",
                                      "Content-Type": "text/plain; charset=\"utf-8\""}}],
                "header": {"parent_document_id": "",
                           "child_document_id": "",
                           "subject": ""}}]},
