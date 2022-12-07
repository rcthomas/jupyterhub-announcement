import React, { useEffect, useState } from "react";
import Toast from "react-bootstrap/Toast";
import { AiOutlineNotification } from "@react-icons/all-files/ai/AiOutlineNotification";
import Col from "react-bootstrap/Col";
import Row from "react-bootstrap/Row";
import ReactMarkdown from "react-markdown";

import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";

import TimeAgo from "javascript-time-ago";

try {
  TimeAgo.addDefaultLocale(en);
} catch (e) {
  console.error(e);
}

export const timeAgo = new TimeAgo("en-US");

var _ = require("lodash");

export const Announcements = ({}) => {
  const stored = JSON.parse(
    localStorage.getItem("dismissedAnnouncements") || "[]"
  );
  const [state, setState] = useState({
    announcements: [],
    // dismissed: new Set(),
    dismissed: new Set(stored),
  });
  console.log(state);

  const fetchAnnouncements = () => {
    fetch("/services/announcement/list", {
      method: "GET",
      redirect: "manual",
      credentials: "same-origin",
    })
      .then((response) => {
        if (!response.ok) {
          console.error("Error fetching announcements", response);
        }
        return response.json();
      })
      .then((announcements) => {
        setState((prev) => ({
          ...prev,
          announcements: announcements,
        }));
      })
      .catch((error) => {
        console.error("Error getting announcements", error);
      });
  };

  const toggleClose = (announcement) => {
    state.dismissed.add(announcement.timestamp);
    localStorage.setItem(
      "dismissedAnnouncements",
      JSON.stringify(Array.from(state.dismissed))
    );
    setState((prev) => ({
      ...prev,
      dismissed: state.dismissed,
    }));
  };

  useEffect(() => {
    fetchAnnouncements();
    const intervalId = setInterval(() => fetchAnnouncements(), 3600 * 5 * 1000);
    return () => clearInterval(intervalId);
  }, []);

  if (_.isEmpty(state.announcements)) return null;

  const toasts = state.announcements.flatMap((announcement, index) => {
    if (state.dismissed.has(announcement.timestamp)) return [];

    return [
      <Toast
        key={`toast-${index}`}
        onClose={() => toggleClose(announcement)}
        className="mb-1"
        style={{ width: "100%" }}
      >
        <Toast.Header>
          <Row style={{ width: "99%" }}>
            <Col>
              <strong>
                <AiOutlineNotification size={25} />
                {"  Announcement"}
              </strong>
            </Col>
            <Col md="auto">
              <small>
                {timeAgo.format(Date.parse(announcement.timestamp.concat("Z")))}
              </small>
            </Col>
          </Row>
        </Toast.Header>

        <Toast.Body>
          {announcement.announcement.split("\\").map((p, index) => (
            <ReactMarkdown
              key={`ann-${announcement.timestamp}-${index}`}
              children={p.replace("\\", "")}
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeRaw]}
            />
          ))}
        </Toast.Body>
      </Toast>,
    ];
  });
  if (_.isEmpty(toasts)) return null;
  return (
    <div
      aria-live="polite"
      aria-atomic="true"
      className="mb-3 position-relative"
    >
      {toasts}
    </div>
  );
};
